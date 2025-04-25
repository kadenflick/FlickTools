import arcpy
import os
import json
import itertools
import requests

from pathlib import Path
from typing import Literal, Any, Generator, Iterator
from enum import Enum

import utils.constants as constants

###
#  TODO: 
#   - Improve toolbox config
#   - Improve create file function
#   - Maybe turn controlCLSID into a dataclass
#       - Having issues with the enum
###

#################################################
# TOOLBOX
#################################################

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
    
def toolbox_abspath(path: os.PathLike) -> os.PathLike:
    """
    Get absolute path for file within toolbox.

    The path parameter is the relative path to a file within the top-level
    toolbox folder.
    """

    return os.path.join(Path(__file__).parents[1].absolute(), path)

#################################################
# ARCPY
#################################################

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

    Tool functions must still return a list of parameters because the
    parameters list is rebuilt each time it is passed between tool
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
    
def load_fieldmap(path: os.PathLike) -> arcpy.FieldMappings:
    """Create a Field Mappings object from a .fieldmap file."""

    with open(path, 'r') as fieldmap:
        return arcpy.FieldMappings().loadFromString(fieldmap.read())
    
def arcgis_rest_query(url: str, query: dict[str, Any], max_records: int) -> dict[str, Any]:
    """
    Query ArcGIS REST service and return all records, regardless of
    service record limit.
    """

    # Set up variables
    resp = {}
    if "resultOffset" not in query.keys(): query["resultOffset"] = 0

    # Loop until all records are collected
    while True:
        # Get result of query and store the whole things or portions of it as needed
        cur_resp = requests.get(url, query).json()

        if not resp:
            resp = cur_resp
        else:
            resp["features"].extend(cur_resp["features"])

        # Check if all records in query have been collected
        if "exceededTransferLimit" not in cur_resp.keys() or not cur_resp["exceededTransferLimit"]:
            break
        else:
            query["resultOffset"] += max_records

    return resp

#################################################
# FILE IO
#################################################

def sanitize_filename(filename: str) -> str:
    """Sanitize a filename."""

    return "".join([char for char in filename if char.isalnum() or char in [' ', '_', '-']])

def create_file(complete_path: str) -> str:
    """Validates file path and creates directory if necessary."""

    # Split path
    head, tail = os.path.split(complete_path)

    # Create directory if it doesn't exist
    if not os.path.exists(head):
        os.mkdir(head)

    return os.path.join(head, tail)

def delete_scratch_names(scratch_names: list[Any]) -> list[Any]:
    """
    Attempt to delete scratch names. Return any names that could not
    be deleted.
    """

    # Attempt to delete names
    return [name for name in scratch_names if not arcpy.Exists(name) or not arcpy.Delete_management(name)]

#################################################
# PRINTING
#################################################

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

def pretty_format(input_list: list[str], header: str = None, prefix: str = None, sort: bool = True,
                  max_width: int = 100, max_columns: int = 4, min_columns: int = 1, target_len_column: int = 10) -> Iterator[str]:
    """
    Consolidate a list of strings into a list of formated strings of a specific
    length that end with a newline to make printing the list look nicer.
    """

    # Sort input if idicated
    if sort: input_list = sorted(input_list, key=lambda s: s.upper())

    # Determine number of columns and lengths
    len_sorted_input = len(input_list)
    len_longest_item = max([len(i) for i in input_list])
    num_columns = max(min_columns, min(int(max_width // len_longest_item), min(int(len_sorted_input / target_len_column), max_columns)))
    base_height, remainder = divmod(len_sorted_input, num_columns)
    last_reduced = max(0, (num_columns - 1) - remainder)
    num_cols_increased = last_reduced + remainder
    column_lengths = [base_height + (i < num_cols_increased) for i in range(num_columns - 1)] + [base_height - last_reduced]

    # Consolidate items in input_list for printing
    input_interator = iter(input_list)
    columns = [list(itertools.islice(input_interator, i)) for i in column_lengths]

    # Add header to start of columns if there is one
    if header:
        for c in columns: c[:0] = [header, "—" * max(len(header), max([len(i) for i in c], default=0))]
    
    # Determine padding for each column
    padding = [max([len(value) for value in column], default=0) for column in columns]

    # Zip and return padded rows
    for row in itertools.zip_longest(*columns, fillvalue=""):
        padded_column = [value.ljust(pad) for value, pad in zip(row, padding)]

        yield f"{prefix if prefix else ''}{f'{constants.TAB}'.join(padded_column)}\n"