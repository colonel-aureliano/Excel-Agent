from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional, Type, Dict
import re

app = FastAPI()

# Define a Base Action Model
class Action(BaseModel):
    type: str  # Defines the type of action (e.g., "Select", "Set", etc.)
    reg: Optional[str] = None  # Regular expression (optional)

    def to_string(self):
        base_string = f"{self.type.upper()} {self._format_params()}"
        return f"REGEX ^.*$ | {base_string}" if not self.reg else f"REGEX {self.reg} | {base_string}"

    def _format_params(self):
        return ""


# Define Specific Actions
class Select(Action):
    type: str = "Select"
    col1: str
    row1: int
    col2: str
    row2: int

    def _format_params(self):
        return f"{self.col1}{self.row1}:{self.col2}{self.row2}"


class SelectAndDrag(Action):
    type: str = "SelectAndDrag"
    col1: str
    row1: int
    col2: str
    row2: int

    def _format_params(self):
        return f"{self.col1}{self.row1}:{self.col2}{self.row2}"


class Format(Action):
    type: str = "Format"
    style: str

    def _format_params(self):
        return self.style


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
        return "No parameters"


# Reverse Parsing Function
def parse_action_string(action_str: str) -> List[Action]:
    action_classes: Dict[str, Type[Action]] = {
        "SELECT": Select,
        "SELECTANDDRAG": SelectAndDrag,
        "FORMAT": Format,
        "SET": Set,
        "TOOLACTION": ToolAction,
        "TELLUSER": TellUser,
        "TERMINATE": Terminate,
    }

    actions = []
    action_strings = re.split(r"[\n;]+", action_str.strip())  # Split by newlines or semicolons
    
    for action_entry in action_strings:
        match = re.match(r"REGEX (.*?) \| (\w+) (.+)", action_entry.strip())
        if match:
            reg, action_type, params = match.groups()
            action_type = action_type.upper()
            if action_type in action_classes:
                
                if action_type == "SELECT" or action_type == "SELECTANDDRAG":
                    param_match = re.match(r"(\D+)(\d+):(\D+)(\d+)", params)
                    if param_match:
                        col1, row1, col2, row2 = param_match.groups()
                        action = action_classes[action_type](reg=reg, col1=col1, row1=int(row1), col2=col2, row2=int(row2))
                        actions.append(action)

                elif action_type == "FORMAT":
                    action = Format(reg=reg, style=params)
                    actions.append(action)
                
                elif action_type == "SET":
                    action = Set(reg=reg, text=params)
                    actions.append(action)
                
                elif action_type == "TOOLACTION":
                    action = ToolAction(reg=reg, tool=params)
                    actions.append(action)
                
                elif action_type == "TELLUSER":
                    action = TellUser(reg=reg, message=params)
                    actions.append(action)
                
                elif action_type == "TERMINATE":
                    action = Terminate(reg=reg)
                    actions.append(action)

    return actions

def generate_action_string(actions: List[Action]) -> str:
    return "\n".join(action.to_string() for action in actions)


# Example usage:
if __name__ == "__main__":
    actions = [
        Select(reg="^A.*", col1="A", row1=1, col2="B", row2=-1),
        SelectAndDrag(reg="^C.*", col1="C", row1=2, col2="D", row2=6),
        Format(style="Bold"),
        Set(text="Hello, World!"),
        ToolAction(tool="Copy"),
        TellUser(message="Operation completed."),
        Terminate(),
        Format(style="Italic")  # Example without reg
    ]

    input_string = generate_action_string(actions)
    # input_string = "REGEX ^A.* | SELECT A1:B5; REGEX ^C.* | SELECTANDDRAG C2:D6; REGEX ^Bold.* | FORMAT Bold"

    parsed_actions = parse_action_string(input_string)
    for action in parsed_actions:
        print(action.to_string())
