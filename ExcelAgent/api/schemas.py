from typing import Optional, List, Union
from dataclasses import dataclass, field

from pydantic import BaseModel, Field
from .action_schemas import *

class MessageRequest(BaseModel):
    role: str
    message: str

class MessageResponse(BaseModel):
    role: str = Field(default=None)
    message: str = Field(default=None)

############################################## Subtask Instruction

class SubtaskInstructionRequest(BaseModel):
    role: str
    message: str
    #TODO: feed first_n_rows_of_sheet into LLM, adjust prompt accordingly
    first_n_rows_of_sheet: List[List[Union[str, int, float, bool, None]]] = Field(default=None)
    read_context: Optional[str] = Field(default=None, description="Context from previous Read actions that were executed")

class Action(BaseModel):
    type: str  # Defines the type of action (e.g., "Select", "Set", etc.)

    def to_string(self):
        return f"{self.type.upper()}: {self._format_params()}"

    def _format_params(self):
        return ""

class ActionsResponse(BaseModel):
    role: str = Field(default=None)
    message: str = Field(default=None)
    actions: List[Union[Select, SelectAndDrag, Format, Set, ToolAction, TellUser, Terminate, Read]]  = Field(default=None)


