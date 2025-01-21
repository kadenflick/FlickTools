import arcpy
import requests

from typing import Any

import utils.archelp as archelp
import utils.constants as constants
from utils.tool import Tool

class ZoomToCounty_map(Tool):
    def __init__(self) -> None:
        """ Zooms the current map view to the extent of a specific county in the US. """
        # Initialize base class parameters
        super().__init__()

        # Tool parameters
        self.label = "Zoom To County"
        self.alias = "ZoomToCounty_map"
        self.description = "Zooms the current map view to the extent of a specific county in the US."
        self.category = "Navigation"
        self.service_URL = "https://services.arcgis.com/P3ePLMYs2RVChkJx/ArcGIS/rest/services/USA_Census_Counties/FeatureServer/0/query"

        return

    def getParameterInfo(self) -> list[arcpy.Parameter]:
        """ Define the tool parameters. """
        # Define parameters
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

        county = arcpy.Parameter(
            displayName = "County",
            name = "county",
            datatype = "GPString",
            parameterType = "Required",
            direction = "Input"
        )
        county.filter.type = "ValueList"
        
        return [state, county]
    
    def updateParameters(self, parameters: list[arcpy.Parameter]) -> None:
        """ 
        Modify the values and properties of parameters before internal 
        validation is performed.
        """
        # Load parameters in a useful format
        parameters = archelp.Parameters(parameters)

        # Get list of counties from service
        if parameters.state.altered and not parameters.state.hasBeenValidated:
            try:
                query = {
                    "where": f"STATE_ABBR = '{constants.STATE_ABBR(parameters.state.valueAsText)}'",
                    "returnGeometry": "false",
                    "outFields": "NAME",
                    "f": "pjson"
                }
                resp = requests.get(self.service_URL, query).json()
                parameters.county.filter.list = sorted([i['attributes']['NAME'] for i in resp['features']])
            # Catch the same errors here that we do in update messages
            except:
                pass

        return
    
    def updateMessages(self, parameters: list[arcpy.Parameter]) -> None:
        """ Modify the messages created by internal validation for each tool parameter. """
        # Load parameters in a useful format
        parameters = archelp.Parameters(parameters)

        # See if we can hit the service with a barebones query
        if parameters.state.altered and not parameters.state.hasBeenValidated:
            try:
                query = {
                    "where": "1=1",
                    "returnGeometry": "false",
                    "outFields": "OBJECTID",
                    "resultRecordCount": "1",
                    "f": "pjson"
                }
                resp = requests.get(self.service_URL, query).json()
            # Need to be more specific here, not great to just have a blanket except
            # Need to do this here because internal validation overwrites errors set in updateParameters
            except:
                parameters.state.setErrorMessage("Unable to connect to service. This tool requires an internet connection.")
                parameters.county.setErrorMessage("Unable to connect to service. This tool requires an internet connection.")

        return
    
    def execute(self, parameters: list[arcpy.Parameter], messages: list[Any]) -> None:
        """ The source code of the tool. """
        # Load parameters and define current view
        parameters = archelp.Parameters(parameters)
        current_view = self.project.activeView

        # Change camera extent and zoom
        if current_view is not None:
            # Get extent of specified county from service
            # Need some error handling here
            state = constants.STATE_ABBR(parameters.state.valueAsText)
            county = parameters.county.valueAsText
            query = {
                "where": f"STATE_ABBR = '{state}' AND NAME LIKE '{county}%'",
                "returnExtentOnly": "true",
                "outSR": f"{current_view.map.spatialReference.factoryCode}",
                "f": "pjson"
            }
            resp = requests.get(self.service_URL, query).json()
            ext_list = [resp['extent'][i] for i in ['xmin','ymin','xmax','ymax']]

            # Print some value messages to the geoprocessing window.
            archelp.arcprint(f"WHERE: {query['where']}\nWKID: {query['outSR']}\nEXTENT: {ext_list}")
            
            # Set the map extent using the extent recieved from the REST request if it is valid.
            if "NaN" not in ext_list:
                ext = arcpy.Extent(XMin = resp['extent']['xmin'], YMin = resp['extent']['ymin'], 
                                   XMax = resp['extent']['xmax'], YMax = resp['extent']['ymax'], 
                                   spatial_reference = arcpy.SpatialReference(resp['extent']['spatialReference']['latestWkid']))
                current_view.camera.setExtent(ext)
            else:
                archelp.arcprint("Error: Invalid extent. Check tool parameters.", severity="ERROR")
        else:
            archelp.arcprint("Error: No map view selected. Select a map view before running tool.", severity="ERROR")
        
        return