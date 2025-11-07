from ExcelAgent.chat.prompt import get_action_prompt, get_reflect_prompt, get_process_prompt
from ExcelAgent.chat.api import inference_chat
from ExcelAgent.chat.chat import init_action_chat, init_reflect_chat, init_memory_chat, add_response
from ExcelAgent.agents.agent_state import AgentState

def action_agent_response(subtask_inst, excel_file_path, agent_state: AgentState, add_info):
    last_summary = agent_state.summary_history[-1] if agent_state.summary_history else ""
    last_action = agent_state.action_history[-1] if agent_state.action_history else ""
    prompt_action = get_action_prompt(
        subtask_inst,
        excel_file_path,
        agent_state.thought_history,
        agent_state.summary_history,
        agent_state.action_history,
        last_summary,
        last_action,
        agent_state.reflection_thought,
        add_info,
        agent_state.error_flag,
        agent_state.completed_requirements,
        agent_state.memory,
        agent_state.use_som,
        agent_state.icon_caption,
        agent_state.location_info,
    )

    chat_action = init_action_chat()
    chat_action = add_response("user", prompt_action, chat_action)

    output_action = inference_chat(
        chat_action, 
        agent_state.vl_model_version, 
        agent_state.api_url, 
        agent_state.api_token,
        provider=agent_state.model_provider,
        temperature=agent_state.temperature
    )
    thought = (
        output_action.split("### Thought ###")[-1]
        .split("### Action ###")[0]
        .replace("\n", " ")
        .replace(":", "")
        .replace("  ", " ")
        .strip()
    )
    action = (
        output_action.split("### Action ###")[-1]
        .split("### Operation ###")[0]
        .replace("\n", " ")
        .replace("  ", " ")
        .strip()
    )
    summary = (
        output_action.split("### Operation ###")[-1]
        .replace("\n", " ")
        .replace("  ", " ")
        .strip()
    )
    chat_action = add_response("assistant", output_action, chat_action)
    status = "#" * 50 + " Decision " + "#" * 50
    print(status)
    print(output_action)
    print('#' * len(status))

    return thought, summary, action

def reflect_agent_response(subtask_inst, thought, summary, action, excel_file_path, agent_state: AgentState, add_info):
    prompt_reflect = get_reflect_prompt(subtask_inst, excel_file_path, summary, action, add_info)
    chat_reflect = init_reflect_chat()
    chat_reflect = add_response("user", prompt_reflect, chat_reflect)

    output_reflect = inference_chat(
        chat_reflect, 
        agent_state.vl_model_version, 
        agent_state.api_url, 
        agent_state.api_token,
        provider=agent_state.model_provider,
        temperature=agent_state.temperature
    )
    reflection_thought = (
        output_reflect.split("### Thought ###")[-1]
        .split("### Answer ###")[0]
        .replace("\n", " ")
        .strip()
    )
    reflect = output_reflect.split("### Answer ###")[-1].replace("\n", " ").strip()
    chat_reflect = add_response("assistant", output_reflect, chat_reflect)
    status = "#" * 50 + " Reflection " + "#" * 50
    print(status)
    print(output_reflect)
    print('#' * len(status))

    if 'A' in reflect:
        agent_state.thought_history.append(thought)
        agent_state.summary_history.append(summary)
        agent_state.action_history.append(action)

        prompt_planning = get_process_prompt(
            subtask_inst,
            agent_state.thought_history,
            agent_state.summary_history,
            agent_state.action_history,
            agent_state.completed_requirements,
            add_info,
        )
        chat_planning = init_memory_chat()
        chat_planning = add_response("user", prompt_planning, chat_planning)
        output_planning = inference_chat(
            chat_planning, 
            agent_state.vl_model_version, 
            agent_state.api_url, 
            agent_state.api_token,
            provider=agent_state.model_provider,
            temperature=agent_state.temperature
        )
        chat_planning = add_response("assistant", output_planning, chat_planning)
        status = "#" * 50 + " Planning " + "#" * 50
        print(status)
        print(output_planning)
        print('#' * len(status))
        agent_state.completed_requirements = (
            output_planning.split("### Completed contents ###")[-1].replace("\n", " ").strip()
        )
        agent_state.error_flag = False

    elif 'B' in reflect:
        agent_state.error_flag = True
        # presskey('esc')

    elif 'C' in reflect:
        agent_state.error_flag = True
        # presskey('esc')

    else:
        agent_state.thought_history.append(thought)
        agent_state.summary_history.append(summary)
        agent_state.action_history.append(action)
        prompt_planning = get_process_prompt(
            subtask_inst,
            agent_state.thought_history,
            agent_state.summary_history,
            agent_state.action_history,
            agent_state.completed_requirements,
            add_info,
        )
        chat_planning = init_memory_chat()
        chat_planning = add_response("user", prompt_planning, chat_planning)
        output_planning = inference_chat(
            chat_planning, 
            agent_state.vl_model_version, 
            agent_state.api_url, 
            agent_state.api_token,
            provider=agent_state.model_provider,
            temperature=agent_state.temperature
        )
        chat_planning = add_response("assistant", output_planning, chat_planning)
        status = "#" * 50 + " Planning " + "#" * 50
        print(status)
        print(output_planning)
        print('#' * len(status))
        agent_state.completed_requirements = (
            output_planning.split("### Completed contents ###")[-1].replace("\n", " ").strip()
        )

    return reflection_thought