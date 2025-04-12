import os
import google.generativeai as genai

script_dir = os.path.dirname(os.path.abspath(__file__))
one_shot_prompt_path = os.path.join(script_dir, "one_shot_prompt.txt")

with open(one_shot_prompt_path, "r", encoding="utf-8") as file:
    one_shot_prompt = file.read()

api_key = os.environ.get("GENAI_API_KEY")
genai.configure(api_key=api_key)

model = genai.GenerativeModel("gemini-2.0-flash")
chat = model.start_chat(history=[])

file = genai.upload_file(os.path.join(script_dir, "action_bnf.txt"))
# The file remains in context as long as you're using the same chat session.

first_chat = True

def gemini_one_shot_response(subtask_instruction):
    global first_chat
    if first_chat:
        response = chat.send_message([file, "\n\n", one_shot_prompt + subtask_instruction])
        first_chat = False
    else:
        response = chat.send_message(one_shot_prompt + subtask_instruction)

    return response.text

if __name__ == "__main__":
    subtask_instruction = "Highlight any element from column C that starts with a question mark."
    response_text = gemini_one_shot_response(subtask_instruction)
    print(response_text)
    # subtask_instruction = "Format to bold the elements in column I that are greater than 5000."
    # response_text = gemini_one_shot_response(subtask_instruction)
    # print(response_text)