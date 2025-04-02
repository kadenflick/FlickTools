import arcpy
import os
import random

from typing import Any, Literal
from abc import ABC
from collections import defaultdict

import utils.archelp as archelp
import utils.constants as constants

class Tool(ABC):
    """Base class for all tools."""
    
    def __init__(self) -> None:
        """Base tool."""

        # Tool parameters
        self.label = "Tool"
        self.description = "Base class for all tools"
        self.canRunInBackground = False
        self.category = "Unassigned"
        self.ft_config = archelp.ToolboxConfig(archelp.toolbox_abspath(r"utils\configs\FlickTools_config.json"))
        self.tool_messages = defaultdict(list)
        
        # Project variables
        self.project = arcpy.mp.ArcGISProject("CURRENT")
        self.project_location = self.project.homeFolder
        self.project_name = os.path.basename(self.project_location)
        
        # Database variables
        self.default_gdb = self.project.defaultGeodatabase
        self.databases = self.project.databases

        return
    
    def _add_tool_message(self, message, severity: Literal['INFO', 'WARNING', 'ERROR'] = 'INFO') -> None:
        """
        Print a message to the geoprocessing window and append to dict
        of tool messages.
        """

        # Append message to tool message and call arcprint to print the message
        self.tool_messages[severity].append(message)
        archelp.arcprint(message, severity=severity)

        return
    
    def _get_complimented(self) -> None:
        """Print a compliment if asked to."""

        # Print compliment with leading newline if there are tool messages
        if self.ft_config.value("get_compliments"):
            out_message = [f"{random.choice(constants.COMPLIMENTS)} :)"]
            if self.tool_messages: out_message.insert(0, "")

            archelp.arcprint("\n".join(out_message))
        
        return
    
    def getParameterInfo(self) -> list[arcpy.Parameter]:
        """Define the tool parameters."""
        return []
    
    def isLicensed(self) -> bool:
        """Set whether the tool is licensed to execute."""
        return True
    
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

    def execute(self, parameters: list[arcpy.Parameter], messages:list[Any]) -> None:
        """The source code of the tool."""
        return

    def postExecute(self, parameters: list[arcpy.Parameter]) -> None:
        """
        This method takes place after outputs are processed and
        added to the display.
        """
        return