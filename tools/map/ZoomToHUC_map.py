import arcpy
import requests

from typing import Any

import utils.archelp as archelp
import utils.constants as constants
from utils.tool import Tool

class ZoomToHUC_map(Tool):
    def __init__(self) -> None:
        """ Zooms the map to a specific HUC in the US."""

        # Initialize base class parameters
        super().__init__()

        # Tool parameters
        self.label = "Zoom To HUC"
        self.alias = "ZoomToHUC_map"
        self.description = "Zooms the map to a specific HUC in the US."
        self.category = "Navigation"
        self.partial_service_URL = "https://hydrowfs.nationalmap.gov/arcgis/rest/services/wbd/MapServer/"

        # USGS feature layer numbers for each HUC layer
        self.huc_layers = {"HUC2": 1, "HUC4": 2, "HUC6": 3, "HUC8": 4, "HUC10": 5, "HUC12": 6, "HUC14": 7, "HUC16": 8}
        
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
        state.filter.list = constants.STATE_NAMES
        state.value = self.ft_config.value("default_state")
        
        huc_level = arcpy.Parameter(
            displayName = "Level",
            name = "huc_level",
            datatype = "GPString",
            parameterType = "Required",
            direction = "Input"
        )
        huc_level.filter.type = "ValueList"
        huc_level.filter.list = list(self.huc_layers.keys())
        huc_level.value = self.ft_config.value("default_huc_level")
        
        huc = arcpy.Parameter(
            displayName = "Watershed",
            name = "huc",
            datatype = "GPString",
            parameterType = "Required",
            direction = "Input"
        )
        huc.filter.type = "ValueList"

        return [state, huc_level, huc]
    
    def updateParameters(self, parameters: list[arcpy.Parameter]) -> None:
        """ 
        Modify the values and properties of parameters before internal 
        validation is performed.
        """

        # Load parameters in a useful format
        parameters = archelp.Parameters(parameters)

        # Update watershed pick list
        if ((parameters.state.altered and not parameters.state.hasBeenValidated)
            or (parameters.huc_level.altered and not parameters.huc_level.hasBeenValidated)):
            try:
                # Get all HUCs in current state from USGS REST 
                layer = self.huc_layers[parameters.huc_level.valueAsText]
                state = constants.STATE_ABBR(parameters.state.valueAsText)
                huc_level = parameters.huc_level.valueAsText.lower()
                base_url = f"{self.partial_service_URL}{layer}/query"
                query = {
                    "where": f"states LIKE '%{state}%'",
                    "returnGeometry": "false",
                    "outFields": f"{huc_level},name",
                    "f": "pjson"
                }
                resp = requests.get(base_url, query).json()

                # Parse response and set list for huc field
                layer_list = [f"{i['attributes']['name']} [{i['attributes'][huc_level]}]" for i in resp['features']]
                parameters.huc.filter.list = sorted(layer_list)
                parameters.huc.value = None
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

        # See if we can hit the service with a barebones query
        # Need to do this here because internal validation overwrites errors set in updateParameters
        if ((parameters.state.altered and not parameters.state.hasBeenValidated)
            or (parameters.huc_level.altered and not parameters.huc_level.hasBeenValidated)):
            try:
                layer = self.huc_layers[parameters.huc_level.valueAsText]
                base_url = f"{self.partial_service_URL}{layer}/query"
                query = {
                    "where": "1=1",
                    "returnGeometry": "false",
                    "outFields": "OBJECTID",
                    "resultRecordCount": "1",
                    "f": "pjson"
                }
                resp = requests.get(base_url, query).json()
            # Need to be more specific here, not great to just have a blanket except
            except:
                parameters.state.setErrorMessage("Unable to connect to service. This tool requires an internet connection.")
                parameters.county.setErrorMessage("Unable to connect to service. This tool requires an internet connection.")

        return
    
    def execute(self, parameters: list[arcpy.Parameter], messages: list[Any]) -> None:
        """The source code of the tool."""
        
        # Load parameters and define current view
        parameters = archelp.Parameters(parameters)
        current_view = self.project.activeView

        # Change camera extent and zoom
        if current_view is not None:
            # Get extent of specified HUC from USGS REST
            # Probably should put a try block in here
            layer = self.huc_layers[parameters.huc_level.valueAsText]
            huc_level = parameters.huc_level.valueAsText.lower()
            huc = parameters.huc.valueAsText.split(" ")[-1][1:-1]
            base_url = f"{self.partial_service_URL}{layer}/query"
            query_params = {
                "where": f"{huc_level} = '{huc}'",
                "returnExtentOnly": "true",
                "outSR": f"{current_view.map.spatialReference.factoryCode}",
                "f": "pjson"
            }
            resp = requests.get(base_url, query_params).json()
            ext_list = [resp['extent'][i] for i in ['xmin','ymin','xmax','ymax']]

            # Print some value messages to the geoprocessing window.
            archelp.arcprint(f"WHERE: {query_params['where']}\nWKID: {query_params['outSR']}\nEXTENT: {ext_list}")
            
            # Set the map extent using the extent recieved from the REST request if it is valid.
            if "NaN" not in ext_list:
                ext = arcpy.Extent(
                    XMin = resp['extent']['xmin'], YMin = resp['extent']['ymin'], 
                    XMax = resp['extent']['xmax'], YMax = resp['extent']['ymax'], 
                    spatial_reference = arcpy.SpatialReference(resp['extent']['spatialReference']['latestWkid'])
                )
                current_view.camera.setExtent(ext)
            else:
                archelp.arcprint("Error: Invalid extent. Check tool parameters.", severity="ERROR")
        else:
            archelp.arcprint("Error: No map view selected. Select a map view before running tool.", severity="ERROR")
        
        return