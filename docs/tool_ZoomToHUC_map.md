[ [FlickTools](../README.md) | [Tool List](Tool_List.md) ]

# Zoom To HUC

Zooms the camera to the extent of a watershed in the US.

**Category:** Navigation<br>
**Source File:** [ZoomToHUC_map.py](../tools/map/ZoomToHUC_map.py)<br>
**Available in:** [FT Everyday](toolbox_FT_Everyday.md)

# Usage

This tool is meant for use in ArcGIS Pro. Before running the tool, select an active map view. If a map view is not selected, the tool will fail and display an error message.

An internet connection is required to run this tool and access the USGS ArcGIS REST API.

## Dialog

Parameters when running the tool through the ArcGIS Pro geoprocessing dialog.

>| Label | Description | Type |
>| :--- | :--- | :--- |
>| State | US State the watershed intersects with. | Text |
>| Level | USGS watershed level, or field. | Text |
>| Watershed | USGS watershed name and code. | Text |