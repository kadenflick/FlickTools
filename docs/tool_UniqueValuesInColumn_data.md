[ [FlickTools](../README.md) | [Tool List](Tool_List.md) ]

# Unique Values In Column

Find all unqiue values in one or more columns of a feature class.

**Category:** General<br>
**Source File:** [UniqueValuesInColumn_data.py](../tools/data/UniqueValuesInColumn_data.py)<br>
**Available in:** [FT Everyday](toolbox_FT_Everyday.md)

# Usage

This tool is meant for use in ArcGIS Pro. To view the output of the tool when *Output as Table* is unchecked, click *View Details* in the geoprocessing pane.

## Dialog

Parameters when running the tool through the ArcGIS Pro geoprocessing dialog.

>| Label | Description | Type |
>| :--- | :--- | :--- |
>| Input Features | Feature that contains one or more fields. | Feature Layer; Table View |
>| Columns to Summarize | The fields to summarize. | Field |
>| Include counts | Indicate if counts of unique values should be included.<ul><li>*Checked:* Counts are included.</li><li>*Unchecked:* Counts are not included. This is the default.</li></ul> | Boolean |
>| Evaluate columns individually | Find unique values in each column individually.<ul><li>*Checked:* Columns are evaluated individually.</li><li>*Unchecked:* Columns are evaluated together. Output returns unique combinations of values across all input columns. This is the default.</li></ul> | Boolean |
>| Export output to Excel | Indicate if output should be exported to an Excel file.<ul><li>*Checked:* Export output to an Excel file.</li><li>*Unchecked:* Do not export output. This the default.</li></ul> | Boolean |
>| Output File *(optional)* | Excel file that will contain tool output. | Table |