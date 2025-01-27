import arcpy
import os
import json

from pathlib import Path
from typing import Literal, Any, Generator
from enum import Enum

class controlCLSID(Enum):
    """
    See [Parameter Controls](https://pro.arcgis.com/en/pro-app/latest/arcpy/geoprocessing_and_python/parameter-controls.htm)
    documentation for more information on parameter controls.
    """
    EXCLUDE_INTERSECT_AND_UNION = '{15F0D1C1-F783-49BC-8D16-619B8E92F668}'
    SLIDER_RANGE = '{C8C46E43-3D27-4485-9B38-A49F3AC588D9}'
    LARGE_NUMBER = '{7A47E79C-9734-4167-9698-BFB00F43AE41}'
    COMPOSITE_SWITCH = '{BEDF969C-20D2-4C41-96DA-32408CA72BF6}'
    MULTILINE = '{E5456E51-0C41-4797-9EE4-5269820C6F0E}'
    MULTIVALUE_CHECKBOX = '{172840BF-D385-4F83-80E8-2AC3B79EB0E0}'
    MULTIVALUE_CHECK_ALL = '{38C34610-C7F7-11D5-A693-0008C711C8C1}'
    FEATURE_LAYER_CREATE = '{60061247-BCA8-473E-A7AF-A2026DDE1C2D}'
    HORIZONTAL_VALUE_TABLE = '{1AA9A769-D3F3-4EB0-85CB-CC07C79313C8}'
    SINGLE_VALUE_TABLE = '{1A1CA7EC-A47A-4187-A15C-6EDBA4FE0CF7}'

class Parameters(list):
    """ 
    Parameters class that replaces the list of parameters in the tool
    functions with an object that can be access the parameters by name,
    index, or attribute.

    You still need tool functions to return a list of parameters as the
    parameters list is rebuilt each time it is passed beteween the tool
    functions. That list can be immediately converted to a Parameters object
    at the beginning of the function.
    """
    def __init__(self, parameters: list[arcpy.Parameter]) -> None:
        self.__dict__.update({parameter.name: parameter for parameter in parameters})
        return
    
    def __iter__(self) -> Generator[arcpy.Parameter, None, None]:
        for value in self.__dict__.values():
            yield value
        return
    
    def __len__(self) -> int:
        return len(self.__dict__)
    
    def __getitem__(self, key) -> arcpy.Parameter:
        if isinstance(key, int):
            return list(self)[key]
        return self.__dict__[key]
    
    def __setitem__(self, key, value) -> None:
        if isinstance(key, int):
            self.__dict__[list(self.__dict__)[key]] = value
        self.__dict__[key] = value
        return
    
    def __getattr__(self, name: str) -> arcpy.Parameter:
        if name in self.__dict__:
            return self.__dict__[name]
        return super().__getattribute__(name)
    
    def append(self, parameter: arcpy.Parameter) -> None:
        if not isinstance(parameter, arcpy.Parameter):
            raise TypeError(f"Parameter must be of type arcpy.Parameter, not {type(parameter)}")
        self.__dict__[parameter.name] = parameter
    
    def extend(self, parameters: list[arcpy.Parameter]) -> None:
        for parameter in parameters:
            self.append(parameter)
    
    def __repr__(self) -> str:
        return str(list(self.__dict__.values()))

class ToolboxConfig():
    """
    Loads a toolbox config file and creates an objeect for accessing the
    config values. Input is the full path to the config file.
    """

    def __init__(self, config_path: os.PathLike) -> None:
        self.config_path = config_path
        self.config_values = self._load_config(config_path)
        return
    
    def _load_config(self, path) -> dict:
        """ Attempt to decode json file. """
        try:
            return json.load(open(path))
        except FileNotFoundError:
            return None
    
    def value(self, index: str) -> str:
        """ Return the config value at the given index. """        
        if(self.config_values and index in self.config_values.keys()):
            return self.config_values[index]["value"]
        return None
    
    def asParameters(self) -> list[arcpy.Parameter]:
        return
    
def sanitize_filename(filename: str) -> str:
    """Sanitize a filename."""

    return "".join([char for char in filename if char.isalnum() or char in [' ', '_', '-']])

def arcprint(*values: object,
             sep: str = " ",
             end: str = "\n",
             file = None,
             flush: bool = False,
             severity: Literal['INFO', 'WARNING', 'ERROR'] = None):
    """
    Print a message to the ArcGIS Pro message queue and stdout set severity
    to 'WARNING' or 'ERROR' to print to the ArcGIS Pro message queue with
    the appropriate severity
    """

    # Print the message to stdout
    print(*values, sep=sep, end=end, file=file, flush=flush)
    
    end = "" if end == '\n' else end
    message = f"{sep.join(map(str, values))}{end}"
    # Print the message to the ArcGIS Pro message queue with the appropriate severity
    match severity:
        case "WARNING":
            arcpy.AddWarning(f"{message}")
        case "ERROR":
            arcpy.AddError(f"{message}")
        case _:
            arcpy.AddMessage(f"{message}")
    return

def load_fieldmap(path: os.PathLike) -> arcpy.FieldMappings:
    """Create a Field Mappings object from a .fieldmap file."""

    with open(path, 'r') as fieldmap:
        return arcpy.FieldMappings().loadFromString(fieldmap.read())
    
def toolbox_abspath(path: os.PathLike) -> os.PathLike:
    """
    Get absolute path for file within toolbox.

    The path parameter is the relative path to a file within the top-level
    toolbox folder.
    """

    return os.path.join(Path(__file__).parents[1].absolute(), path)