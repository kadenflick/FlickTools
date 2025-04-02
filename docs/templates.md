# Tool Template

Use this template to create a new toolbox tool. The naming convention for a tool source file is `NameOfTool_category.py`. New tools should be placed in the approriate category subfolder in the `tools` directory. Once a new tool is created, add it to a toolbox by updating the appropriate `.pyt` file.

```python
import arcpy

from typing import Any

from utils.tool import Tool
import utils.archelp as archelp

class ToolName_category(Tool):
    def __init__(self) -> None:
        """
        Tool Description.
        """

        # Initialize base class parameters
        super().__init__()

        # Tool parameters
        self.label = "Tool Name"
        self.alias = "ToolName_category"
        self.description = "Tool description."
        self.category = "Toolbox Category"

        return
    
    def getParameterInfo(self) -> list[arcpy.Parameter]:
        """Define the tool parameters."""
        return []
    
    def execute(self, parameters: list[arcpy.Parameter], messages: list[Any]) -> None:
        """The source code of the tool."""

        # Load parameters in a useful format
        parameters = archelp.Parameters(parameters)

        # Print a random compliment to the geoprocessing pane if asked to
        self._get_complimented()

        return
```

# Tool Documentation Template

Use this template to document a new tool. The naming convention for a tool documentation file is `tool_NameOfTool_category.md`. New documentation files should be placed in the `docs` directory. Once a new documentation page is created, add a link to the [Tool List](Tool_List.md) under the appropriate category. Once the tool is added to a toolbox, include a link to the tool documention in the toolbox documentation file.

```markdown
[ [FlickTools](../README.md) | [Tool List](Tool_List.md) ]

# Tool Name

Tool description.

**Category:** Tool Category<br>
**Source File:** [NameOfTool_category.py](../tools/category/NameOfTool_category.py)<br>
**Available in:** [Toolbox Name](toolbox_Toolbox_Name.md)

# Usage

This tool is meant for use both in ArcGIS Pro and Python. Other notes about tool useage.

## Dialog

Parameters when running the tool through the ArcGIS Pro geoprocessing dialog.

>| Label | Description | Type |
>| :--- | :--- | :--- |
>| *Attribute* | *Description* | *Type* |

### Derived Output

>| Label | Description | Type |
>| :--- | :--- | :--- |
>| *Attribute* | *Description* | *Type* |

## Python

\```python
FlickTools.<Tool Name>(<Required Input>, {<Optional Input>})
\```

>| Label | Description | Type |
>| :--- | :--- | :--- |
>| *Attribute* | *Description* | *Type* |

### Derived Output

>| Label | Description | Type |
>| :--- | :--- | :--- |
>| *Attribute* | *Description* | *Type* |

### Code Sample
\```python
# Code sample
\```
```