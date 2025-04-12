from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from typing import Dict, Any
from ..utils.utils import get_logger
from .schemas import *

from temp_gemini_api import gemini_one_shot_response
from action_reverse_parse import parse_action_string
from .action_sequence_sample import sample_dispath

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
    logger.info("Received message: "+ request.message)
    subtask_instruction = request.message

    # Choose a sample based on the subtask_instruction
    # actions_response = sample_dispath(subtask_instruction)
    # Issue: cannot find empty column without idea of the content of user's sheet

    # model generates something like the following:
    # REGEX ^.*$ | SELECT C1:C-1 \n REGEX ^\?.*$ | FORMAT style: backgroundcolor, color: yellow
    # use parse_action_string to parse it into list of actions, ready to be sent to front-end

    #TODO replace the below with calling 3 agent LLMs
    actions_response = gemini_one_shot_response(subtask_instruction)
    logger.info("Actions response: " + str(actions_response))
    actions = parse_action_string(actions_response)
    actions_response = ActionsResponse(
        role="assistant",
        message="success",
        actions=actions
    )
    return actions_response