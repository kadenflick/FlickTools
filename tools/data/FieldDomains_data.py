import arcpy

import utils.archelp as archelp
import utils.constants as constants
from utils.tool import Tool

###
#  TODO: 
#   - Pretty print domain values
#   - Can't get domains from rest service endpoints with current setup
###

class FieldDomains_data(Tool):
    def __init__(self) -> None:
        """Displays the domains for one or more fields in a feature."""

        # Initialize base class parameters
        super().__init__()

        # Tool parameters
        self.label = "Field Domains"
        self.alias = "FieldDomains_data"
        self.description = "Displays the domains for one or more fields in a feature."
        self.category = "General"

        return
    
    def getParameterInfo(self) -> list:
        """Define the tool parameters."""

        input_features = arcpy.Parameter(
            displayName = "Input Features",
            name = "input_features",
            datatype = ["GPFeatureLayer", "DEFeatureClass"],
            parameterType = "Required",
            direction = "Input")
        
        fields = arcpy.Parameter(
            displayName = "Field(s)",
            name = "fields",
            datatype = "Field",
            parameterType = "Required",
            direction = "Input",
            multiValue = True)
        fields.parameterDependencies = [input_features.name]

        return [input_features, fields]

    def execute(self, parameters:list[arcpy.Parameter], messages:list) -> None:
        """The source code of the tool."""
        
        # Load parameters in a useful format
        parameters = archelp.Parameters(parameters)
      
        # Get all domains objects and filtered field objects in input features
        feature_properties = arcpy.Describe(parameters.input_features.valueAsText)
        domains = {d.name: d for d in arcpy.da.ListDomains(feature_properties.path)}
        fields = [f for f in feature_properties.fields if f.name in parameters.fields.valueAsText.split(";")]

        # Build output for each input field
        out_message = []
        num_fields = len(fields)

        for counter, field in enumerate(fields):
            out_message.append(f"## FIELD: {field.aliasName} [{field.name}]\n")
            
            # Build info about domain if there is one
            if field.domain in domains:
                domain = domains[field.domain]

                out_message.append((f"{constants.TAB}Domain: {domain.name}\n"
                                    f"{constants.TAB}Type: {domain.domainType}\n"
                                    f"{constants.TAB}Nullable: {field.isNullable}\n\n"))
                
                if domain.domainType == "CodedValue":
                    out_message.append([f"{constants.TAB}{k} : {v}" for k, v in domain.codedValues.items()])
                elif domain.domainType == "Range":
                    out_message.append((f"{constants.TAB}Min: {domain.range[0]}\n"
                                        f"{constants.TAB}Max: {domain.range[1]}\n"))
            else:
                out_message.append(f"{constants.TAB}Domain: <None>\n")

            # Print an extra return if we have more fields to print
            if counter < num_fields - 1: out_message.append("\n")

        # Print output message
        archelp.arcprint("".join(out_message))
        
        return