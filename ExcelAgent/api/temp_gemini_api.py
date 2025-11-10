import os
import google.generativeai as genai
from ..utils.utils import get_logger

logger = get_logger(__name__)

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

def gemini_one_shot_response(subtask_instruction, first_n_rows_of_sheet=None, read_context=None):
    first_n_rows_of_sheet = str(first_n_rows_of_sheet)
    continuing_prompt = f" Now, go ahead, solve this new user instruction in the same fashion: {subtask_instruction}."
    if first_n_rows_of_sheet:
        continuing_prompt += f" Also you may or may not need this, but here are the first several rows of the user's sheet up to the last nonempty column: {first_n_rows_of_sheet}"
    if read_context:
        continuing_prompt += f"\n\nIMPORTANT CONTEXT FROM PREVIOUS READ ACTIONS:\n{read_context}\n\nUse this information to make informed decisions about the current task."
    global first_chat
    prompt = None
    if first_chat:
        prompt = [file, "\n\n", one_shot_prompt + continuing_prompt]
        first_chat = False
    else:
        prompt = [continuing_prompt]
    
    logger.info("Prompt sent to Gemini API: " + str(prompt))
    response = chat.send_message(prompt)

    logger.info("Response from Gemini API: " + response.text)
    return response.text

if __name__ == "__main__":
    subtask_instruction = "Highlight any element from column C that starts with a question mark."
    response_text = gemini_one_shot_response(subtask_instruction)
    print(response_text)
    # subtask_instruction = "Format to bold the elements in column I that are greater than 5000."
    # response_text = gemini_one_shot_response(subtask_instruction)
    # print(response_text)

