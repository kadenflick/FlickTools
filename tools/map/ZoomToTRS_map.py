import arcpy

from typing import Any

import utils.archelp as archelp
import utils.constants as constants
from utils.tool import Tool

class ZoomToTRS_map(Tool):
    def __init__(self) -> None:
        """Zooms the map to a specific Township, Section, and Range."""

        # Initialize base class parameters
        super().__init__()

        # Tool parameters
        self.label = "Zoom to TRS"
        self.alias = "ZoomToTRS_map"
        self.description = "Zooms the map to a specific Township, Section, and Range."
        self.category = "Navigation"

        return
    
    def getParameterInfo(self) -> list[arcpy.Parameter]:
        """ Define the tool parameters. """
        
        state = arcpy.Parameter(
            displayName = "State",
            name = "state",
            datatype = "GPString",
            parameterType = "Required",
            direction = "Input"
        )
        state.filter.type = "ValueList"
        state.filter.list = constants.STATE_NAMES
        state.value = self.ft_config.value("default_state")

        township = arcpy.Parameter(
            displayName = "Township",
            name = "township",
            datatype = "GPString",
            parameterType = "Required",
            direction = "Input"
        )
        township.filter.type = "ValueList"

        range = arcpy.Parameter(
            displayName = "Range",
            name = "range",
            datatype = "GPString",
            parameterType = "Required",
            direction = "Input"
        )
        range.filter.type = "ValueList"

        section = arcpy.Parameter(
            displayName = "Section",
            name = "section",
            datatype = "GPString",
            parameterType = "Optional",
            direction = "Input"
        )
        section.filter.type = "ValueList"

        return [state, township, range, section]
    
    def updateParameters(self, parameters: list[arcpy.Parameter]) -> None:
        """ 
        Modify the values and properties of parameters before internal 
        validation is performed.
        """
        return
    
    def updateMessages(self, parameters: list[arcpy.Parameter]) -> None:
        """
        Modify the messages created by internal validation for each tool
        parameter.
        """
        return
    
    def execute(self, parameters: list[arcpy.Parameter], messages: list[Any]) -> None:
        """The source code of the tool."""
        return