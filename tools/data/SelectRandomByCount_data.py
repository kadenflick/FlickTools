import arcpy
import random

from typing import Any

import utils.archelp as archelp
from utils.tool import Tool

###
#  TODO: 
#   - Add option to zoom to selected features
###

class SelectRandomByCount_data(Tool):
    def __init__(self) -> None:
        """Selects a random subset of rows in a given feature."""

        # Initialize the parent class
        super().__init__()
                
        # Overrides
        self.label = "Select Random By Count"
        self.alias = "SelectRandomByCount_data"
        self.description = "Selects a random subset of rows in a given feature."
        self.category = "Selection"
        
        return
    
    def getParameterInfo(self) -> list:
        """Define the tool parameters."""

        input_feautres = arcpy.Parameter(
            displayName = "Input Features",
            name = "input_features",
            datatype = "GPFeatureLayer",
            parameterType = "Required",
            direction = "Input"
        )
        
        subset_count = arcpy.Parameter(
            displayName = "Subset Count",
            name = "subset_count",
            datatype = "GPLong",
            parameterType = "Required",
            direction = "Input"
        )
        
        selected_count = arcpy.Parameter(
            displayName = "Count",
            name = "selected_count",
            datatype = "GPLong",
            parameterType = "Derived",
            direction = "Output"
        )

        selected_feautres = arcpy.Parameter(
            displayName = "Feature With Selection",
            name = "selected_features",
            datatype = "GPFeatureLayer",
            parameterType = "Derived",
            direction = "Output"
        )
        selected_feautres.parameterDependencies = [input_feautres.name]
        selected_feautres.schema.clone = True

        return [input_feautres, subset_count, selected_count, selected_feautres]

    def updateMessages(self, parameters: list[arcpy.Parameter]) -> None:
        """
        Modify the messages created by internal validation for each tool
        parameter.
        """

        # Load parameters in a useful format
        parameters = archelp.Parameters(parameters)

        # Check if subset count is greater then the count of features in input features
        if parameters.input_features.altered and parameters.subset_count.altered:
            count_input_features = int(arcpy.management.GetCount(parameters.input_features.valueAsText)[0])
            subset_count = int(parameters.subset_count.valueAsText)

            if subset_count > count_input_features:
                parameters.subset_count.setErrorMessage(f"Subset Count is greater than the number of rows in Input Features [{count_input_features}].")

        return

    def execute(self, parameters: list[arcpy.Parameter], messages: list[Any]) -> None:
        """The source code of the tool."""

        # Load parameters and define helpful variables
        parameters = archelp.Parameters(parameters)
        input_features = parameters.input_features.valueAsText
        subset_count = int(parameters.subset_count.valueAsText)
        
        # Select subset from the input features
        #
        # Credit for this portion of the tool can be found at:
        #   https://gis.stackexchange.com/questions/78251/how-to-randomly-subset-x-of-selected-points
        if subset_count != 0:
            oids = [oid for oid, in arcpy.da.SearchCursor (input_features, "OID@")]
            oidFldName = arcpy.Describe(input_features).OIDFieldName
            path = arcpy.Describe(input_features).path
            delimOidFld = arcpy.AddFieldDelimiters(path, oidFldName)
            randOids = random.sample(oids, subset_count)
            oidsStr = ", ".join(map(str, randOids))
            sql = "{0} IN ({1})".format(delimOidFld, oidsStr)
            selected_features = arcpy.SelectLayerByAttribute_management (input_features, "", sql)

            # Update derived parameters and print message to geoprocessing window
            parameters.selected_features.value = selected_features
            count_selected_features = int(arcpy.management.GetCount(selected_features)[0])
        else:
            count_selected_features = 0
            
        arcpy.AddMessage(f"Selected {count_selected_features} features.")

        return