import arcpy
import requests

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
        self.township_service_url = "https://gis.blm.gov/arcgis/rest/services/Cadastral/BLM_Natl_PLSS_CadNSDI/MapServer/1/query"
        self.section_service_url = ""

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
        state.value = self.ft_config.value("default_state")

        # Try to get list of states from feature service
        try:
            query = {
                "where": "1=1",
                "returnGeometry": "false",
                "outFields": "STATEABBR",
                "returnDistinctValues": "true",
                "f": "pjson"
            }
            resp = requests.get(self.township_service_url, query).json()
            state.filter.list = sorted([constants.STATE_NAME(i['attributes']['STATEABBR']) for i in resp['features']])
        # Catch the same errors here that we do in update messages 
        except:
            pass

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

        # Load parameters in a useful format
        parameters = archelp.Parameters(parameters)

        # Update township and range filter lists
        if parameters.state.altered and not parameters.state.hasBeenValidated:
            # try:
            query = {
                "where": f"STATEABBR = '{constants.STATE_ABBR(parameters.state.valueAsText)}'",
                "returnGeometry": "false",
                "outFields": "TWNSHPLAB",
                "f": "pjson"
            }
            resp = requests.get(self.township_service_url, query).json()
            split_lists = [i['attributes']['TWNSHPLAB'].split() for i in resp['features']]

            parameters.township.filter.list = sorted([i[0].replace("T", "") for i in split_lists])
            parameters.range.filter.list = sorted([i[1].replace("R", "") for i in split_lists])
            # Catch the same errors here that we do in update messages 
            # except:
            #     pass

        return
    
    def updateMessages(self, parameters: list[arcpy.Parameter]) -> None:
        """
        Modify the messages created by internal validation for each tool
        parameter.
        """

        # Load parameters in a useful format
        parameters = archelp.Parameters(parameters)

        # See if we can hit the township service with a barebones query
        if ((parameters.state.altered and not parameters.state.hasBeenValidated)
            or (parameters.township.altered and not parameters.township.hasBeenValidated)
            or (parameters.range.altered and not parameters.range.hasBeenValidated)):
            try:
                query = {
                    "where": "1=1",
                    "returnGeometry": "false",
                    "outFields": "OBJECTID",
                    "resultRecordCount": "1",
                    "f": "pjson"
                }
                resp = requests.get(self.township_service_url, query).json()
            # Need to be more specific here, not great to just have a blanket except
            # Need to do this here because internal validation overwrites errors set in updateParameters
            except:
                parameters.state.setErrorMessage("Unable to connect to service. This tool requires an internet connection.")
                parameters.township.setErrorMessage("Unable to connect to service. This tool requires an internet connection.")
                parameters.range.setErrorMessage("Unable to connect to service. This tool requires an internet connection.")
        
        return
    
    def execute(self, parameters: list[arcpy.Parameter], messages: list[Any]) -> None:
        """The source code of the tool."""
        return