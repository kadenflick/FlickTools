from importlib import reload, import_module
from traceback import format_exc
from typing import Dict
from utils.models.tool import Tool

def build_dev_error(label: str, desc: str):
    class Development(object):
        def __init__(self):
            """Placeholder tool for development tools"""

            self.category = "Tools in Development"
            self.label = label
            self.alias = self.label.replace(" ", "")
            self.description = desc
            return
    return Development

def import_tools(tool_dict: dict[str, list[str]]) -> list[object]:
    imports = []
    for project, tools in tool_dict.items():
        for tool in tools:
            try:
                module = import_module(f"{project}.{tool}")
                reload(module)
                tool_class = getattr(module, tool)
                globals()[tool] = tool_class
                imports.append(tool)
            except ImportError:
                dev_error = build_dev_error(tool, format_exc())
                globals()[tool] = dev_error
                imports.append(tool)
    return [v for k, v in globals().items() if k in imports]