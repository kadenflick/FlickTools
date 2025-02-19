import arcpy

import utils.archelp as archelp
import utils.constants as constants
from utils.tool import Tool

###
#  TODO: 
#   - Pretty print domain values
#       - Can probably use the basic version of the formatting function
#       - Maybe put sorting the list in the formatting funcion
#   - Can't get domains from rest service endpoints with current setup
#   - Not sure how this will behave with subtypes
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
            direction = "Input"
        )
        
        fields = arcpy.Parameter(
            displayName = "Field(s)",
            name = "fields",
            datatype = "Field",
            parameterType = "Required",
            direction = "Input",
            multiValue = True
        )
        fields.parameterDependencies = [input_features.name]

        return [input_features, fields]

    def execute(self, parameters:list[arcpy.Parameter], messages:list) -> None:
        """The source code of the tool."""
        
        # Load parameters in a useful format
        parameters = archelp.Parameters(parameters)
      
        # Get all domains objects and filtered field objects in input features
        feature_properties = arcpy.Describe(parameters.input_features.valueAsText)
        domains = {d.name: d for d in arcpy.da.ListDomains(feature_properties.path)}
        fields = dict(sorted({f.aliasName: f for f in feature_properties.fields if f.name in parameters.fields.valueAsText.split(";")}.items())).values()

        # Build output for each input field
        out_message = []

        for field in fields:
            temp_message = [f"## {field.aliasName} [{field.name}]"]
            
            # Build info about domain if there is one
            if field.domain in domains:
                domain = domains[field.domain]

                temp_message.extend([f"{constants.TAB}Domain: {domain.name}",
                                    f"{constants.TAB}Type: {domain.domainType}",
                                    f"{constants.TAB}Nullable: {field.isNullable}\n"])
                
                if domain.domainType == "CodedValue":
                    max_length = len(max([str(k) for k in domain.codedValues.keys()], key=len))
                    temp_message.extend(sorted([f"{constants.TAB}{str(k).ljust(max_length)} : {v}" for k, v in domain.codedValues.items()]))
                elif domain.domainType == "Range":
                    temp_message.extend([f"{constants.TAB}Min: {domain.range[0]}",
                                        f"{constants.TAB}Max: {domain.range[1]}"])
            else:
                temp_message.append(f"{constants.TAB}Domain: <None>")

            # Combine all temp messages and append to output_message
            out_message.append("\n".join(temp_message))

        # Print output message
        archelp.arcprint("\n\n".join(out_message))
        
        return