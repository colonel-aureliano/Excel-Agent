from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from typing import Dict, Any
from ..utils.utils import get_logger
from .schemas import *

from .temp_gemini_api import gemini_one_shot_response
from .action_reverse_parse import parse_action_string
from .action_sequence_sample import sample_dispath

from .exceptions import ActionStrParseError

logger = get_logger(__name__)

router = APIRouter()

# Echo message back
@router.post("/echo", response_model=MessageResponse)
def process_message(request: MessageRequest):
    logger.info("Received message:", request.message)
    response = MessageResponse(role="assistant", message="Hello, the server got your message: " + request.message)
    return response

# Takes a subtask instruction
# Returns an action sequence
@router.post("/subtask-process", response_model=ActionsResponse)
def process_message(request: SubtaskInstructionRequest):
    subtask_instruction = request.message
    first_n_rows_of_sheet = request.first_n_rows_of_sheet
    logger.info("Received subtask_instruction: "+ subtask_instruction)
    logger.info("First n rows of sheet: " + str(first_n_rows_of_sheet))

    # Choose a sample based on the subtask_instruction
    # actions_response = sample_dispath(subtask_instruction)
    # Issue: cannot find empty column without idea of the content of user's sheet

    # model generates something like the following:
    # REGEX ^.*$ | SELECT C1:C-1 \n REGEX ^\?.*$ | FORMAT style: backgroundcolor, color: yellow
    # use parse_action_string to parse it into list of actions, ready to be sent to front-end

    #TODO replace the below with calling 3 agent LLMs
    actions_response = gemini_one_shot_response(subtask_instruction, first_n_rows_of_sheet)
    logger.info("Actions response: " + str(actions_response))
    success = True
    try: 
        actions = parse_action_string(actions_response)
    except ActionStrParseError as e:
        logger.error("Error parsing actions: " + str(e))
        success = False
        actions = []
    actions_response = ActionsResponse(
        role="assistant",
        message="success" if success else "error",
        actions=actions
    )
    return actions_response