import re
from typing import List, Optional
from .action_schemas import *
from .exceptions import ActionStrParseError

cell_ref_pattern = r"([A-Z]+)(-?\d+)"
regex_entry = r"REGEX\s+([^|]+)\s*\|\s*(.*)"

def parse_cell_range(cell_range: str):
    parts = cell_range.split(":")
    if len(parts) == 1:
        col1, row1 = re.match(cell_ref_pattern, parts[0].strip()).groups()
        return col1, row1, col1, "-1"
    elif len(parts) == 2:
        col1, row1 = re.match(cell_ref_pattern, parts[0].strip()).groups()
        col2, row2 = re.match(cell_ref_pattern, parts[1].strip()).groups()
        return col1, row1, col2, row2
    return None

def parse_format_params(param_str: str):
    params = {
        "style": None,
        "color": None,
        "size": None,
        "alignment": None,
        "wrap": None,
        "value_format": None,
        "border": {}
    }

    parts = [p.strip() for p in re.split(r",(?![^{]*\})", param_str)]  # split by comma not in {}

    for part in parts:
        if part.startswith("style: "):
            params["style"] = part[len("style: "):]
        elif part.startswith("color: "):
            params["color"] = part[len("color: "):]
        elif part.startswith("size: "):
            params["size"] = int(part[len("size: "):])
        elif part.startswith("alignment: "):
            params["alignment"] = part[len("alignment: "):]
        elif part.startswith("wrap: "):
            wrap_value = part[len("wrap: "):]
            params["wrap"] = wrap_value == "True"
        elif part.startswith("value_format: "):
            params["value_format"] = part[len("value_format: "):]
        elif part.startswith("border: {") and part.endswith("}"):
            border_str = part[len("border: {"): -1]
            border_parts = [bp.strip() for bp in border_str.split(",")]
            for bp in border_parts:
                side, val = bp.split(":")
                params["border"][side.strip()] = val.strip() == "True"

    return params

def parse_action_entry(entry: str) -> Optional[object]:
    match = re.fullmatch(regex_entry, entry.strip())
    if not match:
        raise ActionStrParseError(f"Invalid action entry: {entry}")
    reg, action_part = match.groups()
    reg = reg.strip()
    action_part = action_part.strip()

    if action_part.startswith("SELECTANDDRAG"):
        _, cell_range = action_part.split(None, 1)
        cell1, cell2 = cell_range.split(":")
        col1, row1 = re.match(cell_ref_pattern, cell1.strip()).groups()
        col2, row2 = re.match(cell_ref_pattern, cell2.strip()).groups()
        return SelectAndDrag(type="SelectAndDrag", reg=reg, col1=col1, row1=row1, col2=col2, row2=row2)

    elif action_part.startswith("SELECT"):
        _, cell_range = action_part.split(None, 1)
        col1, row1, col2, row2 = parse_cell_range(cell_range)
        return Select(type="Select", reg=reg, col1=col1, row1=row1, col2=col2, row2=row2)

    elif action_part.startswith("FORMAT"):
        param_str = action_part[len("FORMAT"):].strip()
        format_kwargs = parse_format_params(param_str)
        return Format(type="Format", reg=reg if reg else None, **format_kwargs)

    elif action_part.startswith("SET"):
        text = action_part[len("SET"):].strip()
        return Set(type="Set", reg=reg, text=text)

    elif action_part.startswith("TOOLACTION"):
        tool_name = action_part[len("TOOLACTION"):].strip()
        return ToolAction(type="ToolAction", reg=reg, tool=tool_name)

    elif action_part.startswith("TELLUSER"):
        message = action_part[len("TELLUSER"):].strip()
        return TellUser(type="TellUser", reg=reg, message=message)

    elif action_part.startswith("TERMINATE"):
        return Terminate(type="Terminate", reg=reg)
    
    elif action_part.startswith("READ"):
        _, cell_range = action_part.split(None, 1)
        col1, row1, col2, row2 = parse_cell_range(cell_range)
        return Read(type="Read", reg=reg, col1=col1, row1=row1, col2=col2, row2=row2)
    
    raise ActionStrParseError(f"Invalid action entry: {entry}")

def parse_action_string(action_string: str) -> List[object]:
    try: 
        action_entries = re.split(r";|\n", action_string)
        parsed_actions = []
        for entry in action_entries:
            if entry.strip():
                action = parse_action_entry(entry)
                if action:
                    parsed_actions.append(action)
    except Exception as e:
        print(f"Error parsing action string: {action_string}")
        raise ActionStrParseError(f"Error parsing action string: {e}")
    return parsed_actions

if __name__ == "__main__":
    from .action_schemas import action_list_to_str
    actions = [Select(col1="C", row1="1", col2="C", row2="-1"),
        Format(
            style="backgroundcolor",
            color="yellow", 
            reg="^\\?.*$"  # Regex to match elements starting with a question mark
        ),
        TellUser(message="I have set background color to yellow for cells that start with question mark in column C.")
    ]
    act_str = action_list_to_str(actions)
    print(act_str)
    # act_str = "asdf"  # malformed
    actions = parse_action_string(act_str)
    print(actions)