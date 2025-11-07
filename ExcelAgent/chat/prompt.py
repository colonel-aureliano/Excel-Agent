from ExcelAgent.utils.utils import read_excel_file

def get_manager_initial_prompt(instruction, excel_file_path, thought_history, summary_history, action_history, completed_content, add_info):
    excel_file = read_excel_file(excel_file_path)
    
    prompt = "### Background ###\n"
    prompt += f"The user has provided the following instruction: \"{instruction}\".\n"
    prompt += "You are an Excel processing assistant. Your role is to analyze the instruction and break it down into clear, sequential subtasks for manipulating the Excel file.\n"
    prompt += f"Current excel file: {excel_file}\n\n"

    prompt += "### Task Description ###\n"
    prompt += "Your task is to decompose the above instruction into smaller, actionable subtasks. Each subtask should target a specific operation on the Excel file (e.g., selecting a range, applying formatting, filtering rows, or performing calculations).\n"

    prompt += "### Output Requirements ###\n"
    prompt += "Provide a list of subtasks with clear and concise descriptions. Each subtask should be formatted as a short sentence. Ensure that the overall set of subtasks, when executed in order, would complete the user's instruction.\n"
    prompt += "For example:\n"
    prompt += "1. Select the range from A1 to D10.\n"
    prompt += "2. Apply left alignment to all selected cells.\n"
    prompt += "3. Filter out rows containing the keyword 'abc'.\n"
    prompt += "4. Summarize the data in a new text cell.\n\n"

    prompt += "### Your Output ###\n"
    prompt += "List the subtasks only, one per line, numbered in order.\n"

    if add_info != "":
        prompt += "### Hint ###\n"
        prompt += "There are hints to help you complete the user\'s instructions. The hints are as follows:\n"
        prompt += add_info
        prompt += "\n\n"

    return prompt

before_action_excel_file = ""

def get_action_prompt(subtask_instruction, excel_file_path, thought_history, summary_history, action_history, last_summary, last_action, reflection_thought, add_info, error_flag, completed_content, memory, use_som, icon_caption, location_info):
    global before_action_excel_file
    excel_file = read_excel_file(excel_file_path)
    before_action_excel_file = excel_file
    
    prompt = "### Background ###\n"
    prompt += f"You are an Excel operating assistant. The current user instruction is: \"{subtask_instruction}\".\n"
    prompt += f"Current excel file: {excel_file}\n\n"
    prompt += "\n\n"

    if len(action_history) > 0:
        prompt += "### History of Operations ###\n"
        prompt += "The following operations have already been executed on the Excel file in sequence:\n"
        for i in range(len(action_history)):
            operation = summary_history[i].split(" to ")[0].strip() if summary_history[i] else "N/A"
            prompt += f"Step {i+1}: Operation: {operation}; Action: {action_history[i]}\n"
        prompt += "\n"
    
    if completed_content != "":
        prompt += "### Progress ###\n"
        prompt += "After completing the history operations, you have the following thoughts about the progress of user\'s instruction completion:\n"
        prompt += "Completed contents:\n" + completed_content + "\n\n"
    
    if memory != "":
        prompt += "### Memory ###\n"
        prompt += "During the operations, you record the following contents on the screenshot for use in subsequent operations:\n"
        prompt += "Memory:\n" + memory + "\n"
    
    if reflection_thought != "":
        prompt += "### The reflection thought of the last operation ###\n"
        prompt += reflection_thought
        prompt += "\n\n"

    if error_flag:
        prompt += "### Last operation ###\n"
        prompt += f"You previously wanted to perform the operation \"{last_summary}\" on this page and executed the Action \"{last_action}\". But you find that this operation does not meet your expectation. You need to reflect and revise your operation this time."
        prompt += "\n\n"
        print(f"You previously wanted to perform the operation \"{last_summary}\" on this page and executed the Action \"{last_action}\". But you find that this operation does not meet your expectation. You need to reflect and revise your operation this time.")
    
    if add_info != "":
        prompt += "### Hint ###\n"
        prompt += "There are hints to help you complete the user\'s instructions. The hints are as follow:\n"
        prompt += add_info
        prompt += "\n\n"

    prompt += "### Task Requirements ###\n"
    prompt += "Based on the current state and the above history, decide the next single operation to perform on the Excel file. "
    prompt += "For certain items that require selection, such as font and font size, direct input is more efficient than scrolling through choices."
    prompt += "You must choose one of the actions below, optionally with an IF condition:\n\n"
    
    prompt += "1. Select: Select one or more boxes by specifying four parameters (col1, row1, col2, row2) that delineate the region of selection. "
    prompt += "**IMPORTANT: The row and column parameters use 0-based indexing matching the DataFrame indices shown in the Excel file summary. "
    prompt += "For example, if the summary shows row index 0 as the first data row, row index 1 as the second data row, etc., use those same indices in Select. "
    prompt += "When you Select a range, it is automatically highlighted with a yellow background color in the file. No additional formatting action is needed.** "
    prompt += "Optionally, append an IF statement to filter the selection (e.g., IF cell value > 10).\n\n"
    
    prompt += "2. Select and Drag: Select a cell's fill handle and drag it to fill a range, defined by four parameters (col1, row1, col2, row2). "
    prompt += "Optionally, include an IF condition to restrict the operation (e.g., IF cell is numeric).\n\n"
    
    prompt += "3. Select Input Field: Select the input field (the formula bar at the top of Excel) for entering text into a cell.\n\n"
    
    prompt += "4. Set: Type a specified text into the input field. The text to set should be provided as a parameter. "
    prompt += "Optionally, include an IF condition (e.g., IF input field is empty).\n\n"
    
    prompt += "5. Copy/Paste/Delete/...: Choose a tool from the right-click context menu to perform operations such as copy, paste, delete, etc. "
    prompt += "You should specify the tool name and any required parameters. Optionally, add an IF condition if needed.\n\n"
    
    prompt += "6. Tell User: Output a textual response directly to the user (this action does not manipulate the Excel file but communicates status or results).\n\n"
    
    prompt += "7. Terminate: End the process if all operations required by the user instruction have been completed.\n\n"
    
    prompt += "### Output Format ###\n"
    prompt += "Your output must be divided into the following three sections:\n"
    prompt += "1. ### Thought ###\n   Describe your reasoning for the chosen operation based on the current state and history.\n"
    prompt += "2. ### Action ###\n   Specify the single operation you will perform. Use the exact action name from the list above and include any parameters in parentheses. "
    prompt += "If using an IF statement, include it at the end in the format 'IF [condition]'.\n"
    prompt += "3. ### Summary ###\n   Provide a brief natural language summary of what this operation will accomplish (e.g., 'Select cells A1:D10 and apply left alignment').\n\n"
    
    prompt += "Ensure that the operation you choose will move the process closer to fulfilling the user's instruction.\n"

    return prompt


def get_reflect_prompt(subtask_inst, excel_file_path, summary, action, add_info):
    excel_file = read_excel_file(excel_file_path)
    
    prompt = "### Background ###\n"    
    prompt += f"You are an Excel operating assistant reviewing the outcome of the recent operation for the instruction: \"{subtask_inst}\".\n"
    
    prompt += "### Before the Operation ###\n"
    prompt += f"Before Excel file status: {before_action_excel_file}\n\n"
    prompt += "Assume that the Excel file was in its previous state prior to the operation.\n\n"
    
    prompt += "### After the Operation ###\n"
    prompt += f"After Excel file status: {excel_file}\n\n"
    prompt += "The operation has been executed. The Excel file now reflects the changes made.\n\n"
   
    prompt += "### Operation Details ###\n"
    prompt += f"Operation Thought: {summary.split(' to ')[0].strip()}\n"
    prompt += f"Operation Action: {action}\n\n"
    
    if add_info:
        prompt += "### Additional Requirements ###\n"
        prompt += f"{add_info}\n\n"
    
    prompt += "### Response Requirements ###\n"
    prompt += "Based on the difference between the before and after states (which you must conclude based on the operation details), decide whether the result meets your expectations.\n"
    prompt += "Choose one of the following responses:\n"
    prompt += "A: The result meets my expectations.\n"
    prompt += "B: The result is incorrect and requires correction.\n"
    prompt += "C: The operation produced no visible change.\n\n"
    
    prompt += "### Output Format ###\n"
    prompt += "Your output should include:\n"
    prompt += "1. ### Thought ###\n"
    prompt += "   Provide your reasoning about why the result does or does not meet expectations.\n"
    prompt += "2. ### Answer ###\n"
    prompt += "   Output a single letter: A, B, or C, corresponding to your judgment.\n"
    
    return prompt


def get_memory_prompt(insight):
    if insight != "":
        prompt  = "### Important Content ###\n"
        prompt += insight
        prompt += "\n\n"
    
        prompt += "### Response Requirements ###\n"
        prompt += "Please think about whether there is any content closely related to ### Important content ### on the current page? If there is, please output the content. If not, please output \"None\".\n\n"
    
    else:
        prompt  = "### Response Requirements ###\n"
        prompt += "Please think about whether there is any content closely related to user\'s instrcution on the current page? If there is, please output the content. If not, please output \"None\".\n\n"
    
    prompt += "### Output Format ###\n"
    prompt += "Your output format is:\n"
    prompt += "### Important content ###\nThe content or None. Please do not repeatedly output the information in ### Memory ###."
    
    return prompt

def get_process_prompt(instruction, thought_history, summary_history, action_history, completed_content, add_info):
    prompt = "### Background ###\n"
    prompt += f"The user instruction is: \"{instruction}\".\n"
    prompt += "You are an Excel operating assistant. You have executed a series of operations to fulfill the instruction.\n\n"
    
    if add_info != "":
        prompt += "### Hint ###\n"
        prompt += "There are hints to help you complete the user\'s instructions. The hints are as follow:\n"
        prompt += add_info
        prompt += "\n\n"
    
    if len(thought_history) > 1:
        prompt += "### History of Operations ###\n"
        prompt += "The following operations have been performed:\n"
        for i in range(len(summary_history)):
            operation = summary_history[i].split(" to ")[0].strip()
            prompt += f"Step {i+1}: [Thought: {thought_history[i]}; Action: {action_history[i]}; Summary: {operation}]\n"
        prompt += "\n"
        
        prompt += "### Progress Thinking ###\n"
        prompt += "After completing the history operations, you have the following thoughts about the progress of user\'s instruction completion:\n"
        prompt += "Completed contents:\n" + completed_content + "\n\n"
        
        prompt += "### Response Requirements ###\n"
        prompt += "Now you need to update the \"Completed contents\". Completed contents is a general summary of the current contents that have been completed based on the ### History of Operations ###.\n\n"
        
        prompt += "### Output Format ###\n"
        prompt += "Your output format is:\n"
        prompt += "### Completed contents ###\nUpdated Completed contents. Don\'t output the purpose of any operation. Just summarize the contents that have been actually completed in the ### History of Operations ###."
        
    else:
        prompt += "### Current Operation Summary ###\n"
        prompt += "To complete the requirements of user\'s instruction, you have performed an operation. Your operation thought and action of this operation are as follows:\n"
        prompt += f"Operation thought: {thought_history[-1]}\n"
        operation = summary_history[-1].split(" to ")[0].strip()
        prompt += f"Operation action: {operation}\n\n"
        
        prompt += "### Response Requirements ###\n"
        prompt += "Now you need to combine all of the above to generate the \"Completed contents\".\n"
        prompt += "Completed contents is a general summary of the current contents that have been completed. You need to first focus on the requirements of user\'s instruction, and then summarize the contents that have been completed.\n\n"
        
        prompt += "### Output Format ###\n"
        prompt += "Your output format is:\n"
        prompt += "### Completed contents ###\nGenerated Completed contents. Don\'t output the purpose of any operation. Just summarize the contents that have been actually completed in the ### Current operation ###.\n"
        
    return prompt