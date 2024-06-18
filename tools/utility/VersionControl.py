import arcpy
import subprocess
import os

from utils.tool import Tool
from utils import archelp
from utils import models

WORKDIR = os.path.join(os.path.dirname(__file__), "..")
BRANCHES = \
    subprocess.run(
        ["git", "branch", "-a"], 
        cwd=WORKDIR, 
        capture_output=True, 
        text=True
    ).stdout.strip().replace('*',' ').split("\n  ")

def get_status() -> str:
    try:
        status = \
            subprocess.run(
                ["git", "status"], 
                cwd=WORKDIR, 
                capture_output=True, 
                text=True
            ).stdout.strip()
        return status
    except subprocess.CalledProcessError as e:
        return f"Error: {e}"

class VersionControl(Tool):
    
    def __init__(self) -> None:
        super().__init__()
        self.label = "Update Toolboxes"
        self.description = "Runs a git pull on the toolboxes directory to update the tools."
        self.category = "Verson Control"
        
        self.toolboxdir = WORKDIR
        try:
            self.active_branch = \
                subprocess.run(
                    ["git", "branch", "--show-current"], 
                    cwd=self.toolboxdir, 
                    capture_output=True,
                    text=True
                    ).stdout.strip()
            self.branches = [branch.strip() for branch in BRANCHES]
        except subprocess.CalledProcessError as e:
            self.branches = ["Error"]
            self.active_branch = "Error"
            self.status = e
        return
    
    def getParameterInfo(self) -> list:
        branch = arcpy.Parameter(
            displayName="Branch",
            name="branch",
            datatype="GPString",
            parameterType="Optional",
            direction="Input",
            category=self.active_branch,
        )
        branch.value = self.active_branch
        branch.filter.type = "ValueList"
        branch.filter.list = self.branches
        
        status = arcpy.Parameter(
            displayName="Status",
            name="status",
            datatype="GPString",
            parameterType="Optional",
            direction="Input",
            category=self.active_branch
        )
        status.controlCLSID='{E5456E51-0C41-4797-9EE4-5269820C6F0E}'
        status.value = get_status()
        
        return [branch, status]
    
    def updateParameters(self, parameters: list) -> None:
        params = archelp.Parameters(parameters)
        
        if self.active_branch != params.branch.valueAsText:
            # Checkout the selected branch
            try:
                subprocess.run(
                    ["git", "checkout", params.branch.valueAsText],
                    cwd=self.toolboxdir,
                    capture_output=True,
                    text=True
                )
                self.updateParameters(parameters)
            except subprocess.CalledProcessError as e:
                params.branch.addErrorMessage(f"Error checking out branch: {e}")
        
        params.status.value = get_status()
        
        return parameters
    
    def execute(self, parameters:list, messages:list) -> None:
        # Get the path to the toolboxes directory
        toolbox_dir = os.path.join(os.path.dirname(__file__), "..")
        # Run git pull
        result = subprocess.run(["git", "pull"], cwd=toolbox_dir, capture_output=True, text=True)
        archelp.message(result.stdout)
        if result.stderr:
            archelp.message(result.stderr, "error")
        return