[ [FlickTools](../README.md) | [Tool List](Tool_List.md) ]

# Zoom To TRS

Zooms the camera to the extent of a township, range, and section.

**Category:** General<br>
**Source File:** [ZoomToTRS_map.py](../tools/map/ZoomToTRS_map.py)<br>
**Available in:** [FT Everyday](toolbox_FT_Everyday.md)

# Usage

This tool is meant for use in ArcGIS Pro. Before running the tool, select an active map view. If a map view is not selected, the tool will fail and display an error message.

An internet connection is required to run this tool and access the BLM ArcGIS REST API.

## Dialog

Parameters when running the tool through the ArcGIS Pro geoprocessing dialog.

>| Label | Description | Type |
>| :--- | :--- | :--- |
>| State | State with township to zoom to. | Text |
>| Township | Township and range to zoom to. | Text |
>| Section *(optional)* | Section to zoom to. | Text |