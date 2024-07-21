# Toolbox

## Configuration

All toolboxes can access any tools in any tool module through a configuration dictionary:
```python
TOOLS =\
{
    "development":
        [
            "DevTool",
            "GDBMerger",
        ],
    "utilities":
        [
            "VersionControl",
        ],
    "production":
        [
            "VertexBuffer",
        ]
}
```
The `tools` base module is implied, but you can modify this by specifying the base module in the import call:
```python
base_module = 'my_tools'
IMPORTS: list[type[Tool]] = import_tools(TOOLS, base_module)
```
Adding or removing tools is as simple as adding an entry for their parent module to the tools dictonary:
```python
TOOLS =\
{
    "development":
        [
            "DevTool",
            "GDBMerger",
        ],
    "utilities":
        [
            "VersionControl",
        ],
    "production":
        [
            "VertexBuffer",
        ],
    "my_tools":
        [
            "MyExampleTool",
        ],
}
```
Removing tools can be done by commenting out the line it is declared on:
```python
TOOLS =\
{
    "development":
        [
            "DevTool",
            "GDBMerger",
        ],
    "utilities":
        [
            "VersionControl",
        ],
    "production":
        [
            "VertexBuffer",
        ],
    "my_tools":
        [
            #"MyExampleTool",
        ],
}
```
Because this import system relies only on a python dictionary, you can easily move the tool declarations for a toolbox into a config file and control that however you want (e.g. with another toolbox, or through some internal system that exports to a `json` or `toml` file). That would make the `TOOLS` declaration look something like this:
```python
TOOLS = load_tool_config('toolbox_config.json')
```
For now keeping the tool declarations in code is easiest for developemnt because the toolbox itself should have some form of clear list of tools. Otherwise it can be difficult to quickly tell which tools you are including.