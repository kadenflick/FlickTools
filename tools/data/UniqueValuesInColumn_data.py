import arcpy
import os
import pandas as pd

from typing import Any

from utils.tool import Tool
import utils.archelp as archelp
import utils.constants as constants

###
#  TODO: 
#   - Provide option to print domain values, not domain codes
#   - Improve printing
#       - Correctly justify column headers and values
#       - Potentially split output into multiple sets of columns
#   - Improve excel export formatting
#   - Replace whitespace characters with a meaningful value
#       - Potentially set whitespace to nan and then specifify what nan should be in output
###

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

        individual_eval = arcpy.Parameter(
            displayName = "Evaluate columns individually",
            name = "individual_eval",
            datatype = "Boolean",
            parameterType = "Required",
            direction = "Input"
        )
        individual_eval.value = False

        output_as_excel = arcpy.Parameter(
            displayName = "Export output to Excel",
            name = "output_as_excel",
            datatype = "Boolean",
            parameterType = "Required",
            direction = "Input"
        )
        output_as_excel.value = False
        
        output_file = arcpy.Parameter(
            displayName = "Output File",
            name = "output_file",
            datatype = "DEFile",
            parameterType = "Required",
            direction = "Output",
            enabled = False
        )
        output_file.filter.list = ["xlsx", "xls"]

        return [input_features, fields, include_counts, individual_eval, output_as_excel, output_file]
    
    def updateParameters(self, parameters: list[arcpy.Parameter]) -> None:
        """ 
        Modify the values and properties of parameters before internal 
        validation is performed.
        """

        # Load parameters in a useful format
        parameters = archelp.Parameters(parameters)

        # Autogenerate an outfile name if there are input features
        if parameters.input_features.altered and not parameters.output_file.altered:
            file_name = f"{os.path.basename(parameters.input_features.valueAsText)}_UniqueValues.xlsx"
            parameters.output_file.value = os.path.join(self.project_location, file_name)

        # If checkbox to output as table has been checked, enable output table parameter for editing
        if not parameters.output_as_excel.value:
            parameters.output_file.enabled = False
        elif parameters.output_as_excel.value:
            parameters.output_file.enabled = True

        return
    
    def evaluate_dataframe(self, input_df: pd.DataFrame, include_counts: bool, columns: list[str] = None) -> pd.DataFrame:
        """
        Evaluate the input dataframe for duplicates. Include counts if
        indicated.
        """
        
        # Find duplicates in dataframe
        evaluated_dataframe = input_df.value_counts(columns, sort=False).reset_index()
        evaluated_dataframe.rename(columns={"count": "Count"}, inplace=True)

        # If indicated, drop count column
        if not include_counts:
            evaluated_dataframe.drop(columns="Count", inplace=True)

        return evaluated_dataframe
        

    def execute(self, parameters: list[arcpy.Parameter], messages: list[Any]) -> None:
        """The source code of the tool."""

        # Load parameters in a useful format
        parameters = archelp.Parameters(parameters)

        # Load input features to a pandas dataframe
        column_names = parameters.fields.valueAsText.split(";")

        with arcpy.da.SearchCursor(parameters.input_features.valueAsText, column_names) as cursor:
            input_df = pd.DataFrame((row for row in cursor), columns=column_names)

        # Evaluate all columns together or individually as indicated
        include_counts = parameters.include_counts.value

        if parameters.individual_eval.value:
            evaluated_dataframes = {column: self.evaluate_dataframe(input_df, include_counts, column) for column in column_names}    
        else:
            evaluated_dataframes = {"All Input Columns": self.evaluate_dataframe(input_df, include_counts, column_names)}

        # Print output to geoprocessing pane
        formatted_output = []

        for column, df in evaluated_dataframes.items():
            df_strings = [f"{constants.TAB}{s}" for s in df.to_string(index=False).split("\n")]

            formatted_output.append("\n".join([
                f"## FIELD: {column}",
                f"{constants.TAB}Unique combinations: {len(df.index)}",
                "",
                df_strings[0],
                f"{constants.TAB}{'-' * (len(df_strings[0]) - len(constants.TAB))}",
                "\n".join(df_strings[1:])
            ]))
        
        self._add_tool_message("\n\n".join(formatted_output))

        # Write output to excel file if indicated
        if parameters.output_as_excel.value:
            output_file = archelp.create_file(parameters.output_file.valueAsText)

            with pd.ExcelWriter(output_file, mode="w", engine="openpyxl") as writer:
                for sheet, df in evaluated_dataframes.items():
                    df.to_excel(writer, sheet, index=False)

        # Print a random compliment to the geoprocessing pane if asked to
        self._get_complimented()

        return