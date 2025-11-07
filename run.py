import os
import time
import copy
import shutil
import re

from ExcelAgent.chat.api import inference_chat
from ExcelAgent.chat.prompt import get_manager_initial_prompt, get_memory_prompt
from ExcelAgent.chat.chat import init_action_chat, init_reflect_chat, init_memory_chat, add_response
from ExcelAgent.chat.response import action_agent_response, reflect_agent_response
from ExcelAgent.agents.agent_state import AgentState

import argparse

parser = argparse.ArgumentParser(description="Excel Agent")
parser.add_argument('--instruction', type=str, default='default')
parser.add_argument('--excel_file_path', type=str, default='default.xlsx')
parser.add_argument('--font_path', type=str, default="/System/Library/Fonts/Times.ttc")
parser.add_argument('--pc_type', type=str, default="mac") # windows or mac

# Model selection arguments
parser.add_argument('--model_provider', type=str, default='gemini', 
                    choices=['openai', 'gemini', 'deepseek', 'claude'],
                    help="LLM provider to use (default: gemini)")
parser.add_argument('--model_name', type=str, default='gemini-2.0-flash-exp',
                    help="Specific model name (default: gemini-2.0-flash-exp)")
parser.add_argument('--api_key', type=str, help="API key for the selected model provider (or set GEMINI_API_KEY/OPENAI_API_KEY env var)")
parser.add_argument('--api_url', type=str, help="Optional: Custom API URL (for OpenAI-compatible APIs)")
parser.add_argument('--temperature', type=float, default=0.0, help="Model temperature (default: 0.0)")

# Legacy arguments for backwards compatibility
parser.add_argument('--api_token', type=str, help="Deprecated: Use --api_key instead")
parser.add_argument('--qwen_api', type=str, default='', help="Input your Qwen-VL api if icon_caption=1.")
parser.add_argument('--add_info', type=str, default='')
parser.add_argument('--disable_reflection', action='store_true')
parser.add_argument('--max_iters', type=int, default=20)
parser.add_argument('--stagnation_patience', type=int, default=3)

args = parser.parse_args()

if args.pc_type == "mac":
    ctrl_key = "command"
    search_key = ["command", "space"]
    ratio = 2
else:
    ctrl_key = "ctrl"
    search_key = ["win", "s"]
    ratio = 1
    args.font_path = "C:\Windows\Fonts\\times.ttf"

####################################### Model Configuration #########################################

# Handle API key from args or environment
api_key = args.api_key or args.api_token
if not api_key:
    import os
    # Try to get from environment based on provider
    env_key_map = {
        'gemini': 'GEMINI_API_KEY',
        'openai': 'OPENAI_API_KEY',
        'claude': 'CLAUDE_API_KEY',
        'deepseek': 'DEEPSEEK_API_KEY'
    }
    env_var = env_key_map.get(args.model_provider, 'GEMINI_API_KEY')
    api_key = os.environ.get(env_var)
    if not api_key:
        print(f"Error: No API key provided. Please set {env_var} environment variable or use --api_key argument.")
        exit(1)

# Set up model configuration
model_provider = args.model_provider
model_name = args.model_name
temperature = args.temperature

# Set API URL based on provider if not explicitly provided
if args.api_url:
    api_url = args.api_url
else:
    # Default URLs for different providers
    api_url_map = {
        'openai': 'https://api.openai.com/v1/chat/completions',
        'gemini': None,  # Gemini uses google.generativeai SDK directly
        'deepseek': 'https://api.deepseek.com/v1/chat/completions',
        'claude': 'https://api.anthropic.com/v1/messages'
    }
    api_url = api_url_map.get(model_provider)

# For backwards compatibility
vl_model_version = model_name
API_url = api_url
token = api_key

####################################### Edit your Setting #########################################

if args.instruction != 'default':
    instruction = args.instruction
else:
    # Your default instruction
    instruction = "Create a new doc on Word, write a brief introduction of Alibaba, and save the document."
    # instruction = "Help me download the pdf version of the 'Mobile Agent v2' paper on Chrome."

excel_file_path = args.excel_file_path

# Choose between "api" and "local". api: use the qwen api. local: use the local qwen checkpoint
caption_call_method = "api"

# Choose between "qwen-vl-plus" and "qwen-vl-max" if use api method. Choose between "qwen-vl-chat" and "qwen-vl-chat-int4" if use local method.
caption_model = "qwen-vl-max"

# If you choose the api caption call method, input your Qwen api here
qwen_api = args.qwen_api

# You can add operational knowledge to help Agent operate more accurately.
if args.add_info == '':
    add_info = '''
    When searching in the browser, click on the search bar at the top.
    The input field in WeChat is near the send button.
    When downloading files in the browser, it's preferred to use keyboard shortcuts.
    '''
else:
    add_info = args.add_info

# Reflection Setting: If you want to improve the operating speed, you can disable the reflection agent. This may reduce the success rate.
reflection_switch = True if not args.disable_reflection else False

# Memory Setting: If you want to improve the operating speed, you can disable the memory unit. This may reduce the success rate.
memory_switch = False # default: False
###################################################################################################

### Load caption model ###
if caption_call_method == "local":
    # Import heavy dependencies only if needed for local model loading
    import torch
    from modelscope import snapshot_download, AutoModelForCausalLM, AutoTokenizer, GenerationConfig
    
    device = "cuda"
    torch.manual_seed(1234)
    
    if caption_model == "qwen-vl-chat":
        model_dir = snapshot_download('qwen/Qwen-VL-Chat', revision='v1.1.0')
        model = AutoModelForCausalLM.from_pretrained(model_dir, device_map=device, trust_remote_code=True).eval()
        model.generation_config = GenerationConfig.from_pretrained(model_dir, trust_remote_code=True)
    elif caption_model == "qwen-vl-chat-int4":
        qwen_dir = snapshot_download("qwen/Qwen-VL-Chat-Int4", revision='v1.0.0')
        model = AutoModelForCausalLM.from_pretrained(qwen_dir, device_map=device, trust_remote_code=True,use_safetensors=True).eval()
        model.generation_config = GenerationConfig.from_pretrained(qwen_dir, trust_remote_code=True, do_sample=False)
    else:
        print("If you choose local caption method, you must choose the caption model from \"Qwen-vl-chat\" and \"Qwen-vl-chat-int4\"")
        exit(0)
    tokenizer = AutoTokenizer.from_pretrained(qwen_dir, trust_remote_code=True)
elif caption_call_method == "api":
    pass
else:
    print("You must choose the caption model call function from \"local\" and \"api\"")
    exit(0)

###################################################################################################

# thought_history = []
# summary_history = []
# action_history = []
# reflection_thought = ""
# completed_requirements = ""
# memory = ""
# insight = ""
# temp_file = "temp"

# if os.path.exists(temp_file):
#     shutil.rmtree(temp_file)
# os.mkdir(temp_file)
# error_flag = False

agent_state = AgentState()
agent_state.vl_model_version = vl_model_version
agent_state.api_url = API_url
agent_state.api_token = token
agent_state.model_provider = model_provider
agent_state.temperature = temperature

###################################################################################################

# Start main loop

iter = 0
prev_subtask_list = None
stagnation = 0
done = False
while True:
    iter += 1

    if iter > args.max_iters:
        print(f"Max iterations reached: {args.max_iters}. Exiting.")
        break

    prompt_manager = get_manager_initial_prompt(
        instruction,
        excel_file_path,
        agent_state.thought_history,
        agent_state.summary_history,
        agent_state.action_history,
        agent_state.completed_requirements,
        add_info,
    )
    # TODO: Replace with real manager LLM call and parsing to subtask_list
    # For now, use the instruction directly as a single subtask to bypass the manager agent
    manager_agent_response = "..."
    subtask_list = [instruction]  # Use actual instruction instead of placeholder
    print("Subtask list: ", subtask_list)

    if prev_subtask_list == subtask_list:
        stagnation += 1
        if stagnation >= args.stagnation_patience:
            print("No progress detected across iterations. Exiting.")
            break
    else:
        stagnation = 0
        prev_subtask_list = subtask_list

    for subtask_inst in subtask_list:
        thought, summary, action = action_agent_response(
            subtask_inst, excel_file_path, agent_state, add_info
        )

        # Check if agent is asking user for input
        if "Tell User" in action or "TellUser" in action:
            # Extract the message from the action string
            # First try to match quoted content inside Tell User()
            match = re.search(r'Tell\s*User\s*\(\s*["\'](.+?)["\']\s*\)', action, re.IGNORECASE | re.DOTALL)
            if not match:
                # Fallback: try to find content between first ( and last )
                match = re.search(r'Tell\s*User\s*\((.+)\)', action, re.IGNORECASE | re.DOTALL)
            
            if match:
                message = match.group(1).strip('"\'')
                print(f"\n🤖 Agent: {message}")
                user_response = input("👤 Your response: ").strip()
                
                # Update instruction with user's response
                if user_response:
                    instruction = user_response
                    print(f"\nContinuing with your instruction: {instruction}\n")
                    
                    # Record the interaction in agent state
                    agent_state.thought_history.append(thought)
                    agent_state.summary_history.append(summary)
                    agent_state.action_history.append(action)
                    
                    # Add user's response to completed requirements so agent knows the question was answered
                    if agent_state.completed_requirements:
                        agent_state.completed_requirements += f" User provided clarification: {user_response}."
                    else:
                        agent_state.completed_requirements = f"User clarified their request: {user_response}."
                    
                    # Clear error flags and reflection to start fresh with new instruction
                    agent_state.error_flag = False
                    agent_state.reflection_thought = ""
                    
                    # Continue to next iteration with updated instruction
                    break  # Break from subtask loop to restart with new instruction
                else:
                    print("No input provided. Exiting.")
                    done = True
                    break

        # TODO: Execute the parsed 'action' against Excel here

        time.sleep(2)  # wait for the action to be executed

        if "Terminate" in action:
            print("Terminate action detected. Exiting.")
            done = True
            break

        if memory_switch:
            prompt_memory = get_memory_prompt(agent_state.insight)
            chat_mem = init_memory_chat()
            chat_mem = add_response("user", prompt_memory, chat_mem)
            output_memory = inference_chat(
                chat_mem, 
                vl_model_version, 
                API_url, 
                token,
                provider=model_provider,
                temperature=temperature
            )
            chat_mem = add_response("assistant", output_memory, chat_mem)
            status = "#" * 50 + " Memory " + "#" * 50
            print(status)
            print(output_memory)
            print('#' * len(status))
            output_memory = (
                output_memory.split("### Important content ###")[-1].split("\n\n")[0].strip() + "\n"
            )
            if "None" not in output_memory and output_memory not in agent_state.memory:
                agent_state.memory += output_memory

        if reflection_switch:
            agent_state.reflection_thought = reflect_agent_response(
                subtask_inst, thought, summary, action, excel_file_path, agent_state, add_info
            )

    if done:
        break