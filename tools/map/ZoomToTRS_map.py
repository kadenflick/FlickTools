import arcpy
import requests

from typing import Any

import utils.archelp as archelp
import utils.constants as constants
from utils.tool import Tool

###
#  TODO: 
#   - Fix issue with not getting all available townships
#   - Improve and expand error checking and handling
#   - Parse individual columns instead of label column
#       - Allows pulling of PLSS ID in single call to service
#       - Might reduce number of calls to service.
###

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
        self.section_service_url = "https://gis.blm.gov/arcgis/rest/services/Cadastral/BLM_Natl_PLSS_CadNSDI/MapServer/2/query"

        return
    
    def getParameterInfo(self) -> list[arcpy.Parameter]:
        """Define the tool parameters."""
        
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

        section = arcpy.Parameter(
            displayName = "Section",
            name = "section",
            datatype = "GPString",
            parameterType = "Optional",
            direction = "Input"
        )
        section.filter.type = "ValueList"

        return [state, township, section]

    def _multiple_replace(self, text: str) -> str:
        """Replace mutiple characters in a string."""

        # This is basically to clean up Oregon values that include both T and R and have some hyphenated township labels
        subs = {"T": "", "R": "", "-": ""}

        return "".join([subs[c] if c in subs.keys() else c for c in text])
    
    def updateParameters(self, parameters: list[arcpy.Parameter]) -> None:
        """ 
        Modify the values and properties of parameters before internal 
        validation is performed.
        """

        # Load parameters and set useful variables
        parameters = archelp.Parameters(parameters)
        state_abbr = constants.STATE_ABBR(parameters.state.valueAsText)

        # Update township filter list
        if parameters.state.altered and not parameters.state.hasBeenValidated:
            try:
                query = {
                    "where": f"STATEABBR = '{state_abbr}'",
                    "returnGeometry": "false",
                    "outFields": "TWNSHPLAB",
                    "f": "pjson"
                }
                resp = requests.get(self.township_service_url, query).json()
                parameters.township.filter.list = sorted([self._multiple_replace(i['attributes']['TWNSHPLAB']) for i in resp['features']])
            # Catch the same errors here that we do in update messages 
            except:
                pass

        # Update section filter list
        if parameters.township.altered and not parameters.township.hasBeenValidated:
            try:
                # Query township service to get township id
                split_township = parameters.township.valueAsText.split()
                query = {
                    "where": f"STATEABBR = '{state_abbr}' AND TWNSHPLAB LIKE '%{split_township[0]}%{split_township[1]}'",
                    "returnGeometry": "false",
                    "outFields": "PLSSID",
                    "f": "pjson"
                }
                resp = requests.get(self.township_service_url, query).json()
                plss_id = resp["features"][0]["attributes"]["PLSSID"]

                # Query sections service to get list of sections that match township id
                query = {
                    "where": f"PLSSID = '{plss_id}'",
                    "returnGeometry": "false",
                    "outFields": "FRSTDIVLAB",
                    "f": "pjson"
                }
                resp = requests.get(self.section_service_url, query).json()
                parameters.section.filter.list = sorted([i["attributes"]["FRSTDIVLAB"] for i in resp["features"]])
            # Catch the same errors here that we do in update messages 
            except:
                pass

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
            or (parameters.section.altered and not parameters.section.hasBeenValidated)):
            try:
                query = {
                    "where": "1=1",
                    "returnGeometry": "false",
                    "outFields": "OBJECTID",
                    "resultRecordCount": "1",
                    "f": "pjson"
                }
                requests.get(self.township_service_url, query)

                query = {
                    "where": "1=1",
                    "returnGeometry": "false",
                    "outFields": "OBJECTID",
                    "resultRecordCount": "1",
                    "f": "pjson"
                }
                requests.get(self.section_service_url, query)
            # Need to be more specific here, not great to just have a blanket except
            # Need to do this here because internal validation overwrites errors set in updateParameters
            except:
                parameters.state.setErrorMessage("Unable to connect to service. This tool requires an internet connection.")
                parameters.township.setErrorMessage("Unable to connect to service. This tool requires an internet connection.")
                parameters.section.setErrorMessage("Unable to connect to service. This tool requires an internet connection.")
        
        return
    
    def execute(self, parameters: list[arcpy.Parameter], messages: list[Any]) -> None:
        """The source code of the tool."""

        # Load parameters and define helpful variables
        parameters = archelp.Parameters(parameters)
        current_view = self.project.activeView
        split_township = parameters.township.valueAsText.split()
        state_abbr = constants.STATE_ABBR(parameters.state.valueAsText)

        # Change camera extent and zoom
        if current_view is not None:
            # Get appropriate extent from service
            # Need some error handling here
            if not parameters.section.altered:
                query = {
                    "where": f"STATEABBR = '{state_abbr}' AND TWNSHPLAB LIKE '%{split_township[0]}%{split_township[1]}'",
                    "returnExtentOnly": "true",
                    "outSR": f"{current_view.map.spatialReference.factoryCode}",
                    "f": "pjson"
                }
                resp = requests.get(self.township_service_url, query).json()
            else:
                query = {
                    "where": f"STATEABBR = '{state_abbr}' AND TWNSHPLAB LIKE '%{split_township[0]}%{split_township[1]}'",
                    "returnGeometry": "false",
                    "outFields": "PLSSID",
                    "f": "pjson"
                }
                resp = requests.get(self.township_service_url, query).json()
                plss_id = resp["features"][0]["attributes"]["PLSSID"]

                query = {
                    "where": f"PLSSID = '{plss_id}' AND FRSTDIVLAB = '{parameters.section.valueAsText}'",
                    "returnExtentOnly": "true",
                    "outSR": f"{current_view.map.spatialReference.factoryCode}",
                    "f": "pjson"
                }
                resp = requests.get(self.section_service_url, query).json()

            ext_list = [resp['extent'][i] for i in ['xmin','ymin','xmax','ymax']]

            # Print some value messages to the geoprocessing window.
            # self._tool_message(f"WHERE: {query['where']}\nWKID: {query['outSR']}\nEXTENT: {ext_list}")
            
            # Set the map extent using the extent recieved from the REST request if it is valid.
            if "NaN" not in ext_list:
                ext = arcpy.Extent(
                    XMin = resp['extent']['xmin'], YMin = resp['extent']['ymin'], 
                    XMax = resp['extent']['xmax'], YMax = resp['extent']['ymax'], 
                    spatial_reference = arcpy.SpatialReference(resp['extent']['spatialReference']['latestWkid'])
                )
                current_view.camera.setExtent(ext)
            else:
                self._add_tool_message("Error: Invalid extent. Check tool parameters.", severity="ERROR")
        else:
            self._add_tool_message("Error: No map view selected. Select a map view before running tool.", severity="ERROR")

        # Print a random compliment to the geoprocessing pane if asked to
        self._get_complimented()

        return