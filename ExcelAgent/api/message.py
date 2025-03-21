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

    # assume message is “Delete any element from the fifth column that starts with a number”
    actions_reponse = ActionsResponse()
    actions_reponse.role = "assistant"
    actions_reponse.message = "I have deleted any element from the fifth column that starts with a number"
    actions_reponse.actions = [
        Select(col1="E", row1=1, col2="E", row2=-1),
        ToolAction(reg="^\d.*",tool="Delete"),
    ]
    return actions_reponse

