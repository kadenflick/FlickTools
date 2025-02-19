[ [FlickTools](../README.md) | [Tool List](Tool_List.md) ]

# Feature To WKT

Converts features to a Well Known Text (WKT) format and generates output strings. Output is printed to the geoprocessing window and copied to the clipboard by default, or optionally output to a text file.

**Category:** Conversion<br>
**Source File:** [FeatureToWKT_data.py](../tools/data/FeatureToWKT_data.py)<br>
**Available in:** [FT Everyday](toolbox_FT_Everyday.md)

# Usage

This tool is meant for use in ArcGIS Pro.

## Dialog

Parameters when running the tool through the ArcGIS Pro geoprocessing dialog.

>| Label | Description | Type |
>| :--- | :--- | :--- |
>| Input Features | Features to convert to WKT format. | Layer |
>| Output Spatial Reference | Coordinate system of output. | Spatial Reference |
>| Copy output to clipboard | Indicates if output should be copied to the clipboard.<ul><li>*Checked:* Output is copied to the clipboard. This is the default.</li><li>*Unchecked:* Output is not copied to the clipboard.</li></ul> | Boolean |
>| Ouput as text file | Indicates if output should be generated as a text file.<ul><li>*Checked:* Output is generated as a text file.</li><li>*Unchecked:* Output is not generated as a text file. This is the default.</li></ul> | Layer |
>| Output File *(optional)* | Location of text file output. | Text File |