from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from typing import Dict, Any
from ..utils.utils import get_logger
from .schemas import *
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

    #choose a sample based on the subtask_instruction
    from .action_sequence_sample import sample_dispath
    actions_response = sample_dispath(subtask_instruction)
    
    #TODO replace above with calling agent LLMs to create actual actions_response

    return actions_response