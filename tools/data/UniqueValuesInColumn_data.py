import arcpy
import os

from typing import Any

from utils.tool import Tool
import utils.archelp as archelp

class UniqueValuesInColumn_data(Tool):
    def __init__(self) -> None:
        """Finds unique values and counts of unique values in one or more columns."""

        # Initialize base class parameters
        super().__init__()

        # Tool parameters
        self.label = "Unique Values In Column"
        self.alias = "UniqueValuesInColumn_data"
        self.description = "Finds unique values and counts of unique values in one or more columns."
        self.category = "General"
        
        return
    
    def getParameterInfo(self) -> list[arcpy.Parameter]:
        """Define the tool parameters."""

        input_features = arcpy.Parameter(
            displayName = "Input Features",
            name = "input_features",
            datatype = ["GPFeatureLayer", "GPTableView"],
            parameterType = "Required",
            direction = "Input"
        )

        fields = arcpy.Parameter(
            displayName = "Columns to Summarize",
            name = "fields",
            datatype = "Field",
            parameterType = "Required",
            direction = "Input",
            multiValue = True
        )
        fields.parameterDependencies = [input_features.name]
        
        include_counts = arcpy.Parameter(
            displayName = "Include counts",
            name = "include_counts",
            datatype = "Boolean",
            parameterType = "Required",
            direction = "Input"
        )
        include_counts.value = False

        output_as_file = arcpy.Parameter(
            displayName = "Save output to file",
            name = "output_as_file",
            datatype = "Boolean",
            parameterType = "Required",
            direction = "Input"
        )
        output_as_file.value = False
        
        output_file = arcpy.Parameter(
            displayName = "Output File",
            name = "output_file",
            datatype = "DEFile",
            parameterType = "Required",
            direction = "Output",
            enabled = False
        )
        output_file.filter.list = ["xlsx", "xls", "csv"]

        return [input_features, fields, include_counts, output_as_file, output_file]
    
    def updateParameters(self, parameters: list[arcpy.Parameter]) -> None:
        """ 
        Modify the values and properties of parameters before internal 
        validation is performed.
        """

        # Load parameters in a useful format
        parameters = archelp.Parameters(parameters)

        # If checkbox to output as table has been checked, enable output table parameter
        if not parameters.output_as_file.value:
            parameters.output_file.enabled = False
        elif parameters.output_as_file.value:
            parameters.output_file.enabled = True

            if parameters.input_features.altered and not parameters.output_file.altered:
                file_name = f"{os.path.basename(parameters.input_features.valueAsText)}_UniqueValues.xlsx"
                parameters.output_file.value = os.path.join(self.project_location, file_name)

        return
    
    def execute(self, parameters: list[arcpy.Parameter], messages: list[Any]) -> None:
        """The source code of the tool."""
        return