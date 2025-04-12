from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional, Type, Dict
import re

app = FastAPI()

# Base Action Model
class Action(BaseModel):
    type: str  # Defines the type of action (e.g., "Select", "Set", etc.)
    reg: Optional[str] = None  # Regular expression (optional)

    def to_string(self):
        base_string = f"{self.type.upper()} {self._format_params()}"
        return f"REGEX ^.*$ | {base_string}" if not self.reg else f"REGEX {self.reg} | {base_string}"

    def _format_params(self):
        return ""


# Specific Actions
class Select(Action):
    type: str = "Select"
    col1: str
    row1: str
    col2: Optional[str] = None
    row2: Optional[str] = None

    def _format_params(self):
        return f"{self.col1}{self.row1}:{self.col2}{self.row2}" if self.col2 and self.row2 else f"{self.col1}{self.row1}"


class SelectAndDrag(Action):
    type: str = "SelectAndDrag"
    col1: str
    row1: str
    col2: str
    row2: str

    def _format_params(self):
        return f"{self.col1}{self.row1}:{self.col2}{self.row2}"


class Format(Action):
    type: str = "Format"
    style: str
    color: Optional[str] = None  # Used for background and font color
    size: Optional[int] = None  # Used for font size
    alignment: Optional[str] = None  # Used for horizontal/vertical alignment
    border: Optional[Dict[str, bool]] = None  # Top, left, bottom, right, vertical, horizontal
    wrap: Optional[bool] = None  # Whether text should wrap
    value_format: Optional[str] = None  # Value format (e.g., currency, percentage)

    def _format_params(self) -> str:
        params = []
        if self.style:
            params.append(f"style: {self.style}")
        if self.color:
            params.append(f"color: {self.color}")
        if self.size:
            params.append(f"size: {self.size}")
        if self.alignment:
            params.append(f"alignment: {self.alignment}")
        if self.border:
            border_str = ", ".join(f"{key}: {value}" for key, value in self.border.items())
            params.append(f"border: {{ {border_str} }}")
        if self.wrap is not None:
            params.append(f"wrap: {self.wrap}")
        if self.value_format:
            params.append(f"value_format: {self.value_format}")
        
        return ", ".join(params) if params else ""


class Set(Action):
    type: str = "Set"
    text: str

    def _format_params(self):
        return self.text


class ToolAction(Action):
    type: str = "ToolAction"
    tool: str

    def _format_params(self):
        return self.tool


class TellUser(Action):
    type: str = "TellUser"
    message: str

    def _format_params(self):
        return self.message


class Terminate(Action):
    type: str = "Terminate"
    
    def _format_params(self):
        return ""

def action_list_to_str(actions: List[Action]) -> str:
    return "\n".join(action.to_string() for action in actions)


# Example usage:
if __name__ == "__main__":
    actions = [
        Select(reg="^A.*", col1="A", row1="1", col2="B", row2="-1"),
        SelectAndDrag(reg="^C.*", col1="C", row1="2", col2="D", row2="6"),
        Format(style="Bold"),
        Set(text="Hello, World!"),
        ToolAction(tool="Copy"),
        TellUser(message="Operation completed."),
        Terminate(),
        Format(style="Italic")  # Example without reg
    ]
    actions2 = [Select(col1="C", row1="1", col2="C", row2="-1"),
        Format(
            style="backgroundcolor",
            color="#FFFF00",  # Yellow background
            reg="^\\?.*$"  # Regex to match elements starting with a question mark
    )]

    input_string = action_list_to_str(actions)
    print(input_string)
    print("---------------------")

    # input_string = "REGEX ^A.* | SELECT A1:B5; REGEX ^C.* | SELECTANDDRAG C2:D6; REGEX ^Bold.* | FORMAT Bold"
    from action_reverse_parse import parse_action_string
    parsed_actions = parse_action_string(input_string)
    for action in parsed_actions:
        print(action.to_string())
