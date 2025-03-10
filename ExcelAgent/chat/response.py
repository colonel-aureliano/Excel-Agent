from prompt import *
from ExcelAgent.chat.api import *
from chat import *
from run import vl_model_version, API_url, token, args, memory, error_flag

def action_agent_response(subtask_inst, excel_file_path, thought_history, summary_history, action_history, completed_requirements, add_info, reflection_thought):
    prompt_action = get_action_prompt(subtask_inst, excel_file_path, thought_history, summary_history, action_history, summary, action, reflection_thought, add_info, error_flag, completed_requirements, memory, args.use_som, args.icon_caption, args.location_info)
    
    chat_action = init_action_chat()
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

    return thought, summary, action

def reflect_agent_response(subtask_inst, thought, summary, action, excel_file_path, thought_history, summary_history, action_history, completed_requirements, add_info):
    prompt_reflect = get_reflect_prompt(subtask_inst, [], [], 0, 0, summary, action, add_info)
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
        
        prompt_planning = get_process_prompt(subtask_inst, thought_history, summary_history, action_history, completed_requirements, add_info)
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
        
        prompt_planning = get_process_prompt(subtask_inst, thought_history, summary_history, action_history, completed_requirements, add_info)
        chat_planning = init_memory_chat()
        chat_planning = add_response("user", prompt_planning, chat_planning)
        output_planning = inference_chat(chat_planning, 'gpt-4o', API_url, token)
        chat_planning = add_response("assistant", output_planning, chat_planning)
        status = "#" * 50 + " Planning " + "#" * 50
        print(status)
        print(output_planning)
        print('#' * len(status))
        completed_requirements = output_planning.split("### Completed contents ###")[-1].replace("\n", " ").strip()
    
    return reflection_thought