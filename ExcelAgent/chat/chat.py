import copy

#TODO modify for our use

def init_action_chat():
    operation_history = []
    sysetm_prompt = "You are a helpful AI PC operating assistant. You need to help me operate the PC to complete the user\'s instruction."
    operation_history.append(["system", [{"type": "text", "text": sysetm_prompt}]])
    return operation_history


def init_reflect_chat():
    operation_history = []
    sysetm_prompt = "You are a helpful AI PC operating assistant."
    operation_history.append(["system", [{"type": "text", "text": sysetm_prompt}]])
    return operation_history


def init_memory_chat():
    operation_history = []
    sysetm_prompt = "You are a helpful AI PC operating assistant."
    operation_history.append(["system", [{"type": "text", "text": sysetm_prompt}]])
    return operation_history


def add_response_old(role, prompt, chat_history, image=None):
    new_chat_history = copy.deepcopy(chat_history)
    content = [
        {
        "type": "text", 
        "text": prompt
        },
    ]
    new_chat_history.append([role, content])
    return new_chat_history


def add_response(role, prompt, chat_history, image=[]):
    new_chat_history = copy.deepcopy(chat_history)
    content = [
        {
        "type": "text", 
        "text": prompt
        },
    ]
    new_chat_history.append([role, content])
    return new_chat_history

def print_status(chat_history):
    print("*"*100)
    for chat in chat_history:
        print("role:", chat[0])
        print(chat[1][0]["text"] + "<image>"*(len(chat[1])-1) + "\n")
    print("*"*100)