# Reloading of modules preformed here to make sure a toolbox refresh also
# reloads all associated modules. A refresh in ArcGIS Pro only reloads the code
# in this .pyt file, not the associated modules

import sys
from pathlib import Path
from importlib import reload

# Manually add the path to the root of the project
ROOT = str(Path(__file__).parents[2].absolute())

# Insert the module roots to the system path
sys.path.insert(0, ROOT) # ../pytframe2
sys.path.insert(1, rf"{ROOT}\tools") # ../pytframe2/tools
sys.path.insert(2, rf"{ROOT}\utils") # ../pytframe2/utils
# NOTE: Add more module paths here if needed

import utils.reloader as pyt_reload_reloader 
import utils.archelp as pyt_reload_archelp
import utils.tool as pyt_reload_tool

# Inline reloader of dynamic modules
[reload(module) for module_name, module in sys.modules.items() if module_name.startswith("pyt_reload")]

# Import the Tool Importer function
from utils.reloader import import_tools

TOOLS = \
{
    "prod":
        [
            "VertexBuffer",
        ],
    "utilities":
        [
            "VersionControl",
        ],
}

IMPORTS = import_tools(TOOLS)
globals().update({tool.__name__: tool for tool in IMPORTS})

class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        
        self.label = "Production Tools"
        self.alias = self.label.replace(" ", "")
        
        # List of tool classes associated with this toolbox
        self.tools = IMPORTS