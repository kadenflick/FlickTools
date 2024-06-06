import arcpy
import os

class Tool(object):
    """
    Base class for all tools that use python objects to build parameters
    """
    def __init__(self) -> None:
        """
        Tool Description
        """
        # Tool parameters
        self.label = "Tool"
        self.description = "Base class for all tools that use python objects to build parameters"
        self.canRunInBackground = False
        self.category = "Unassigned"
        
        # Project variables
        self.project = arcpy.mp.ArcGISProject("CURRENT")
        self.project_location = self.project.homeFolder
        self.project_name = os.path.basename(self.project_location)
        
        # Database variables
        self.default_gdb = self.project.defaultGeodatabase
        self.databases = self.project.databases
        
        return
    
    def getParameterInfo(self) -> list:
        """
        Define parameter definitions
        """
        return []
    
    def isLicensed(self) -> bool:
        """
        Set whether tool is licensed to execute.
        """
        return True
    
    def updateParameters(self, parameters:list) -> None:
        """
        Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed.
        """
        return
    
    def updateMessages(self, parameters:list) -> None:
        """
        Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation.
        """
        return
    
    def execute(self, parameters:list, messages:list) -> None:
        """
        The source code of the tool.
        """
        return
    
    def postExecute(self, parameters:list) -> None:
        """
        This method takes place after outputs are processed and
        added to the display.
        """
        return