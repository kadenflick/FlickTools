import arcpy
import os
import pandas as pd

from typing import Any

import utils.archelp as archelp
from utils.tool import Tool

###
#  TODO: 
#   - Stop output text file being added to project
#       - Might have to manually check for and remove it
#   - Add checkbox to open text file after it is created
###

class FeatureToWKT_data(Tool):
    def __init__(self) -> None:
        """Converts features in to WKT format."""
        
        # Initialize the parent class
        super().__init__()
                
        # Overrides
        self.label = "Feature To WKT"
        self.alias = "FeatureToWKT_data"
        self.description = "Converts features in to WKT format."
        self.category = "Conversion"
        
        # Parameters
        self.params = {}
        
        return
    
    def getParameterInfo(self) -> list:
        """Define the tool parameters."""

        input_features = arcpy.Parameter(
            displayName = "Input Features",
            name = "input_features",
            datatype = "GPFeatureLayer",
            parameterType = "Required",
            direction = "Input"
        )
        
        spatial_reference = arcpy.Parameter(
            displayName = "Output Spatial Reference",
            name = "spatial_reference",
            datatype = "GPSpatialReference",
            parameterType = "Required",
            direction = "Input"
        )

        clipboard_checkbox = arcpy.Parameter(
            displayName = "Copy output to clipboard",
            name = "clipboard_checkbox",
            datatype = "Boolean",
            parameterType = "Required",
            direction = "Input"
        )
        clipboard_checkbox.value = True

        file_checkbox = arcpy.Parameter(
            displayName = "Output as text file",
            name = "file_checkbox",
            datatype = "Boolean",
            parameterType = "Required",
            direction = "Input"
        )
        file_checkbox.value = False

        output_file = arcpy.Parameter(
            displayName = "Output File",
            name = "output_file",
            datatype = "DETextfile",
            parameterType = "Optional",
            direction = "Output",
            enabled = False
        )
        
        return [input_features, spatial_reference, clipboard_checkbox, file_checkbox, output_file]
    
    def updateParameters(self, parameters: list[arcpy.Parameter]) -> None:
        """ 
        Modify the values and properties of parameters before internal 
        validation is performed.
        """

        # Load parameters in a useful format
        parameters = archelp.Parameters(parameters)

        # Update spatial reference to the spatial reference of input features
        if parameters.input_features.altered and not parameters.input_features.hasBeenValidated:
            parameters.spatial_reference.value = arcpy.Describe(parameters.input_features.valueAsText).featureClass.spatialReference.PCSCode

        # Enable or disable output file box depending on whether the checkbox is checked or not
        if parameters.file_checkbox.value:
            parameters.output_file.enabled = True

            if parameters.input_features.altered and not parameters.output_file.altered:
                file_name = f"{os.path.basename(parameters.input_features.valueAsText)}_FeatureToWKT.txt"
                parameters.output_file.value = os.path.join(self.project_location, file_name)
        elif not parameters.file_checkbox.value:
            parameters.output_file.enabled = False
        
        return
    
    def updateMessages(self, parameters: list[arcpy.Parameter]) -> None:
        """
        Modify the messages created by internal validation for each tool
        parameter. This method is called after internal validation.
        """

        # Load parameters in a useful format
        parameters = archelp.Parameters(parameters)

        # Set warning messages if input features meet certain criteria
        if parameters.input_features.altered and arcpy.Describe(parameters.input_features.valueAsText).FIDSet == "":
            parameters.input_features.setWarningMessage("Input features do not have a selection. All features will be converted.")

        return

    def execute(self, parameters: list[arcpy.Parameter], messages: list[Any]) -> None:
        """The source code of the tool."""

        # Load parameters in a useful format
        parameters = archelp.Parameters(parameters)

        # Reproject features into target coordinate system if necessary
        wkt_features = parameters.input_features.valueAsText
        scratch_features = []

        if arcpy.Describe(wkt_features).featureClass.spatialReference.PCSCode != parameters.spatial_reference.value.PCSCode:
            scratch_features = [arcpy.CreateScratchName(suffix=f"_{i}", data_type="FeatureClass", workspace=arcpy.env.scratchGDB) for i in range(2)]
            arcpy.ExportFeatures_conversion(wkt_features, scratch_features[0])
            arcpy.Project_management(scratch_features[0], scratch_features[1], parameters.spatial_reference.value.PCSCode)
            wkt_features = scratch_features[1]

        # Collect WKT strings
        with arcpy.da.SearchCursor(wkt_features, ["SHAPE@WKT"]) as cursor:
            wkt_strings = [row[0] for row in cursor]

        # Print output
        archelp.arcprint("\n".join(wkt_strings))

        # Add output to clipboard
        if parameters.clipboard_checkbox.value:
            pd.DataFrame(wkt_strings).to_clipboard(excel=False, index=False, header=False)

        # Write output to file
        if parameters.file_checkbox.value:
            with open(archelp.create_file(parameters.output_file.valueAsText), "w") as outfile:
                for wkt in wkt_strings:
                    outfile.write(f"{wkt}\n")

        # Clean up
        archelp.delete_scratch_names(scratch_features)

        return