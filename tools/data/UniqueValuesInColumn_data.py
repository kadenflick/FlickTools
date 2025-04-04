import arcpy
import os
import pandas as pd

from typing import Any

from utils.tool import Tool
import utils.archelp as archelp
import utils.constants as constants

###
#  TODO: 
#   - Improve printing
#       - Correctly justify column headers and values
#       - Potentially split output into multiple sets of columns
#   - Improve excel export formatting
#   - Include progressor messages
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

        use_domains = arcpy.Parameter(
            displayName = "Use domain descriptions",
            name = "use_domains",
            datatype = "Boolean",
            parameterType = "Required",
            direction = "Input"
        )
        use_domains.value = True
        
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

        return [input_features, fields, use_domains, include_counts, individual_eval, output_as_excel, output_file]
    
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
    
    def _table_to_dataframe(self, table: str, column_names: pd.DataFrame, replace_domains: bool) -> pd.DataFrame:
        """
        Convert table to pandas DataFrame and replace domain codes and
        values as neccessary.
        """

        # Set up output and domain lookup table
        parsed_rows = []
        feature_info = arcpy.Describe(table)
        domains = {d.name: d.codedValues for d in arcpy.da.ListDomains(feature_info.path) if d.domainType == "CodedValue"}
        lookup = {field.name: domains[field.domain] for field in feature_info.fields if field.name in column_names and field.domain in domains.keys()}

        # Convert to dataframe
        with arcpy.da.SearchCursor(table, column_names) as cursor:
            for row in cursor:
                parsed_row = []

                for index, column in enumerate(column_names):
                    col_value = str(row[index])

                    # Replace row values with domain desriptions if indicated
                    if replace_domains and column in lookup.keys() and row[index] in lookup[column].keys():
                        col_value = str(lookup[column][row[index]])

                    # Replace row values with replacements
                    if col_value in (None, "None"):
                        col_value = "<Null>"
                    elif col_value == "":
                        col_value = "<Empty String>"
                    elif col_value.isspace():
                        col_value = "<Whitespace>"

                    parsed_row.append(col_value)

                # Append to final output
                parsed_rows.append(parsed_row)

        return pd.DataFrame(parsed_rows, columns=column_names)

    def _evaluate_dataframe(self, input_df: pd.DataFrame, include_counts: bool, columns: list[str] = None) -> pd.DataFrame:
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
    
    def _format_dataframe_text(self, input_df: pd.DataFrame) -> list[str]:
        """Format the console output of a dataframe left justified."""

        # Get dataframe columns
        df_columns = input_df.columns.values.tolist()

        # Interate over each column and left justify it
        formatted_columns = []

        for column in df_columns:
            col_text = input_df.to_string(columns=[column], index=False).split("\n")
            max_len = len(max(col_text, key=len))

            formatted_column = [f"{i.strip():<{max_len}}" for i in col_text]
            formatted_columns.append(formatted_column)

        # Combine justified columns to format suitable for printing
        formatted_df = ["  ".join(i) for i in list(zip(*formatted_columns))]

        return formatted_df

    def execute(self, parameters: list[arcpy.Parameter], messages: list[Any]) -> None:
        """The source code of the tool."""

        # Load parameters in a useful format
        parameters = archelp.Parameters(parameters)

        # Load input features to a pandas dataframe
        column_names = parameters.fields.valueAsText.split(";")
        input_df = self._table_to_dataframe(parameters.input_features.valueAsText, column_names, parameters.use_domains.value)

        # Evaluate all columns together or individually as indicated
        include_counts = parameters.include_counts.value

        if parameters.individual_eval.value:
            evaluated_dataframes = {column: self._evaluate_dataframe(input_df, include_counts, column) for column in column_names}    
        else:
            evaluated_dataframes = {"All Input Columns": self._evaluate_dataframe(input_df, include_counts, column_names)}

        # Print output to geoprocessing pane
        formatted_output = []

        for column, df in evaluated_dataframes.items():
            # df_strings = [f"{constants.TAB}{s}" for s in self._format_dataframe_text(df)]
            df_strings = self._format_dataframe_text(df)

            formatted_output.append("\n".join([
                f"## COLUMN: {column}",
                f"{constants.TAB}Feature rows: {arcpy.GetCount_management(parameters.input_features.valueAsText)}",
                f"{constants.TAB}Unique combinations: {len(df.index)}",
                "",
                # df_strings[0],
                # f"{constants.TAB}{'-' * (len(df_strings[0]) - len(constants.TAB))}",
                # "\n".join(df_strings[1:])
                "".join(archelp.pretty_format(
                    input_list=df_strings[1:],
                    header=[df_strings[0], f"{'-' * len(df_strings[0])}"],
                    prefix=constants.TAB
                ))
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