# Tool Template

Use this template to create a new toolbox tool. The naming convention for a tool is `NameOfTool_category.py`. New tools should be placed in the approriate category subfolder in the `tools` directory.

```python
import arcpy

from typing import Any

from utils.tool import Tool
import utils.archelp as archelp

class ToolName_category(Tool):
    def __init__(self) -> None:
        """
        Tool Description
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
        """ Define the tool parameters. """
        return [] 
    
    def execute(self, parameters: list[arcpy.Parameter], messages: list[Any]) -> None:
        """ The source code of the tool. """
        return
```

# Tool Documentation Template

Use this template to create a new toolbox tool. The naming convention for a tool is `NameOfTool_category.md`. New documentation files should be placed in the `docs` directory.

```markdown
test
```