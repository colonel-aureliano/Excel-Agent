from action_schemas import *
from schemas import ActionsResponse
from ..utils.utils import get_logger

logger = get_logger(__name__)

def sample_dispath(subtask_instruction):
    if "1" in subtask_instruction:
        logger.info("Processing sample1")
        actions_response = sample1()
    elif "2" in subtask_instruction:
        logger.info("Processing sample2")
        actions_response = sample2()
    elif "3" in subtask_instruction:
        logger.info("Processing sample3")
        actions_response = sample3()
    elif "4" in subtask_instruction:
        logger.info("Processing sample4")
        actions_response = sample4()
    return actions_response

def sample1():
    actions_reponse = ActionsResponse()
    actions_reponse.role = "assistant"
    actions_reponse.message = "I have highlighted any element from column C that starts with a question mark"
    actions_reponse.actions = [
        Select(col1="C", row1=1, col2="C", row2=-1), # Frontend understands that C-1 means fetching last non-empty row of column C
        Format(
            style="backgroundcolor",
            color="yellow",  # Set the font color to blue
            reg="^\\?.*$"  # Regex to match elements starting with a question mark
        )
    ]
    return actions_reponse

def sample2():
    actions_reponse = ActionsResponse()
    actions_reponse.role = "assistant"
    actions_reponse.message = "I have formatted column A to italic"
    actions_reponse.actions = [
        Select(col1="A", row1=1, col2="A", row2=-1),
        Format(style="Italic")
    ]
    return actions_reponse

def sample3():
    actions_reponse = ActionsResponse()
    actions_reponse.role = "assistant"
    actions_reponse.message = "I have formatted to bold the elements in column I that are greater than 5000"
    actions_reponse.actions = [
        Select(col1="I", row1=1, col2="I", row2=-1),
        Format(reg="^([5-9][0-9]{3}|[1-9][0-9]{4,}).*$", style="Bold")
    ]
    return actions_reponse

def sample4():
    actions_reponse = ActionsResponse()
    actions_reponse.role = "assistant"
    actions_reponse.message = "I have added elements in column J and K, and set the result in column K."
    actions_reponse.actions = [
        Select(col1="L", row1=2),
        Set(text="=J2+K2"),
        SelectAndDrag(
            col1="L", row1=2, col2="L", row2=-1
        ),
        Select(col1="L", row1=2, col2="L", row2=-1),
        ToolAction(
            tool="Copy"
        ),
        Select(col1="K", row1=2, col2="K", row2=-1),
        ToolAction(
            tool="PasteAsValues"
        ),
        Select( col1="L", row1=2, col2="L", row2=-1),  # Select the range to apply the formula
        ToolAction(
            tool="Delete"
        )  # Optional: If you want to delete the original formula in column L after copying
    ]
    return actions_reponse
