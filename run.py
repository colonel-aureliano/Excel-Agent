import os
import time
import copy
import torch
import shutil

from ExcelAgent.api import inference_chat
from ExcelAgent.prompt import get_action_prompt, get_reflect_prompt, get_memory_prompt, get_process_prompt
from ExcelAgent.chat import init_action_chat, init_reflect_chat, init_memory_chat, add_response

from modelscope import snapshot_download, AutoModelForCausalLM, AutoTokenizer, GenerationConfig

import argparse
from key_stroke_handle import *


parser = argparse.ArgumentParser(description="Excel Agent")
parser.add_argument('--instruction', type=str, default='default')
parser.add_argument('--excel_file_path', type=str, default='')
parser.add_argument('--font_path', type=str, default="/System/Library/Fonts/Times.ttc")
parser.add_argument('--pc_type', type=str, default="mac") # windows or mac
parser.add_argument('--api_url', type=str, default="https://api.openai.com/v1/chat/completions", help="GPT-4o api url.")
parser.add_argument('--api_token', type=str, help="Your GPT-4o api token.")
parser.add_argument('--qwen_api', type=str, default='', help="Input your Qwen-VL api if icon_caption=1.")
parser.add_argument('--add_info', type=str, default='')
parser.add_argument('--disable_reflection', action='store_true')

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

vl_model_version = 'gpt-4o'


####################################### Edit your Setting #########################################

if args.instruction != 'default':
    instruction = args.instruction
else:
    # Your default instruction
    instruction = "Create a new doc on Word, write a brief introduction of Alibaba, and save the document."
    # instruction = "Help me download the pdf version of the 'Mobile Agent v2' paper on Chrome."

# Your GPT-4o API URL
API_url = args.api_url

# Your GPT-4o API Token
token = args.api_token

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


def get_perception_infos(screenshot_file, screenshot_som_file, font_path):
    pass

### Load caption model ###
device = "cuda"
torch.manual_seed(1234)
if caption_call_method == "local":
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

thought_history = []
summary_history = []
action_history = []
reflection_thought = ""
summary = ""
action = ""
completed_requirements = ""
memory = ""
insight = ""
temp_file = "temp"
screenshot = "screenshot"

if os.path.exists(temp_file):
    shutil.rmtree(temp_file)
os.mkdir(temp_file)
if not os.path.exists(screenshot):
    os.mkdir(screenshot)
error_flag = False


iter = 0
while True:
    iter += 1

    prompt_action = get_action_prompt(instruction, [], 0, 0, thought_history, summary_history, action_history, summary, action, reflection_thought, add_info, error_flag, completed_requirements, memory, args.use_som, args.icon_caption, args.location_info)
    chat_action = init_action_chat()
    if args.use_som == 1:
        chat_action = add_response("user", prompt_action, chat_action, [])
    else:
        chat_action = add_response("user", prompt_action, chat_action, [])

    output_action = inference_chat(chat_action, vl_model_version, API_url, token)
    thought = output_action.split("### Thought ###")[-1].split("### Action ###")[0].replace("\n", " ").replace(":", "").replace("  ", " ").strip()
    summary = output_action.split("### Operation ###")[-1].replace("\n", " ").replace("  ", " ").strip()
    action = output_action.split("### Action ###")[-1].split("### Operation ###")[0].replace("\n", " ").replace("  ", " ").strip()
    chat_action = add_response("assistant", output_action, chat_action)
    status = "#" * 50 + " Decision " + "#" * 50
    print(status)
    print(output_action)
    print('#' * len(status))
    

    if "Double Tap" in action:
        coordinate = action.split("(")[-1].split(")")[0].split(", ")
        x, y = int(coordinate[0]), int(coordinate[1])
        tap(x, y, 2)

    elif "Triple Tap" in action:
        coordinate = action.split("(")[-1].split(")")[0].split(", ")
        x, y = int(coordinate[0]), int(coordinate[1])
        tap(x, y, 3)

    elif "Tap" in action:
        coordinate = action.split("(")[-1].split(")")[0].split(", ")
        x, y = int(coordinate[0]), int(coordinate[1])
        tap(x, y, 1)

    elif "Shortcut" in action:
        keys = action.split("(")[-1].split(")")[0].split(", ")
        key1, key2 = keys[0].lower(), keys[1].lower()
        shortcut(key1, key2)
    
    elif "Press" in action:
        key = action.split("(")[-1].split(")")[0]
        presskey(key)

    elif "Open App" in action:
        app = action.split("(")[-1].split(")")[0]
        open_app(app)

    elif "Type" in action:
        coordinate = action.split("(")[1].split(")")[0].split(", ")
        x, y = int(coordinate[0]), int(coordinate[1])
        if "[text]" not in action:
            text = action.split("[")[-1].split("]")[0]
        else:
            text = action.split(" \"")[-1].split("\"")[0]
        tap_type_enter(x, y, text)
        
    elif "Stop" in action:
        break
    
    time.sleep(2) # wait for the action to be excuted

    if memory_switch:
        prompt_memory = get_memory_prompt(insight)
        chat_action = add_response("user", prompt_memory, chat_action)
        output_memory = inference_chat(chat_action, vl_model_version, API_url, token)
        chat_action = add_response("assistant", output_memory, chat_action)
        status = "#" * 50 + " Memory " + "#" * 50
        print(status)
        print(output_memory)
        print('#' * len(status))
        output_memory = output_memory.split("### Important content ###")[-1].split("\n\n")[0].strip() + "\n"
        if "None" not in output_memory and output_memory not in memory:
            memory += output_memory
    
    if reflection_switch:
        prompt_reflect = get_reflect_prompt(instruction, [], [], 0, 0, summary, action, add_info)
        chat_reflect = init_reflect_chat()
        chat_reflect = add_response("user", prompt_reflect, chat_reflect, [])

        output_reflect = inference_chat(chat_reflect, vl_model_version, API_url, token)
        reflection_thought = output_reflect.split("### Thought ###")[-1].split("### Answer ###")[0].replace("\n", " ").strip()
        reflect = output_reflect.split("### Answer ###")[-1].replace("\n", " ").strip()
        chat_reflect = add_response("assistant", output_reflect, chat_reflect)
        status = "#" * 50 + " Reflection " + "#" * 50
        print(status)
        print(output_reflect)
        print('#' * len(status))
    
        if 'A' in reflect:
            thought_history.append(thought)
            summary_history.append(summary)
            action_history.append(action)
            
            prompt_planning = get_process_prompt(instruction, thought_history, summary_history, action_history, completed_requirements, add_info)
            chat_planning = init_memory_chat()
            chat_planning = add_response("user", prompt_planning, chat_planning)
            output_planning = inference_chat(chat_planning, 'gpt-4o', API_url, token)
            chat_planning = add_response("assistant", output_planning, chat_planning)
            status = "#" * 50 + " Planning " + "#" * 50
            print(status)
            print(output_planning)
            print('#' * len(status))
            completed_requirements = output_planning.split("### Completed contents ###")[-1].replace("\n", " ").strip()
            
            error_flag = False
        
        elif 'B' in reflect:
            error_flag = True
            # presskey('esc')
            
        elif 'C' in reflect:
            error_flag = True
            # presskey('esc')
    
    else:
        thought_history.append(thought)
        summary_history.append(summary)
        action_history.append(action)
        
        prompt_planning = get_process_prompt(instruction, thought_history, summary_history, action_history, completed_requirements, add_info)
        chat_planning = init_memory_chat()
        chat_planning = add_response("user", prompt_planning, chat_planning)
        output_planning = inference_chat(chat_planning, 'gpt-4o', API_url, token)
        chat_planning = add_response("assistant", output_planning, chat_planning)
        status = "#" * 50 + " Planning " + "#" * 50
        print(status)
        print(output_planning)
        print('#' * len(status))
        completed_requirements = output_planning.split("### Completed contents ###")[-1].replace("\n", " ").strip()