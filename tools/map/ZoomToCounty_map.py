import arcpy

from typing import Any

from utils.tool import Tool
import utils.archelp as archelp

class ZoomToCounty_map(Tool):
    def __init__(self) -> None:
        """ Zooms the current map view to a specific county. """
        # Initialize base class parameters
        super().__init__()

        # Tool parameters
        self.label = "Zoom To County"
        self.alias = "ZoomToCounty_map"
        self.description = "Zooms the current map view to a specific county."
        self.category = "Navigation"
        self.config_path = archelp.toolbox_abspath(r"utils\configs\FT_Everyday_config.json")
        return
    
    def getParameterInfo(self) -> list[arcpy.Parameter]:
        """ Define the tool parameters. """
        # Load toolbox configs
        config = archelp.ToolboxConfig(self.config_path)

        # Define parameters
        state = arcpy.Parameter(
            displayName = "State",
            name = "state",
            datatype = "GPString",
            parameterType = "Required",
            direction = "Input"
        )
        state.value = config.value("default_state")

        county = arcpy.Parameter(
            displayName = "County",
            name = "county",
            datatype = "GPString",
            parameterType = "Required",
            direction = "Input"
        )

        return [state, county]
    
    def updateParameters(self, parameters: list[arcpy.Parameter]) -> None:
        """ 
        Modify the values and properties of parameters before internal 
        validation is performed.
        """
        # Load parameters in a useful format
        parameters = archelp.Parameters(parameters)

        return
    
    def updateMessages(self, parameters: list[arcpy.Parameter]) -> None:
        """ Modify the messages created by internal validation for each tool parameter. """
        # Load parameters in a useful format
        parameters = archelp.Parameters(parameters)

        return
    
    def execute(self, parameters: list[arcpy.Parameter], messages: list[Any]) -> None:
        """ The source code of the tool. """
        return