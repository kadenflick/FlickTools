[ [FlickTools](../README.md) | [Tool List](Tool_List.md) ]

# Select Random Features

Selects a random subset of rows in a given feature. It returns a selection with a random subset of records in the input features.

**Category:** General<br>
**Source File:** [SelectRandomByCount.py](../tools/data/SelectRandomByCount_data.py)<br>
**Available in:** [FT Everyday](toolbox_FT_Everyday.md)

# Usage

This tool is meant for use in ArcGIS Pro.

## Dialog

Parameters when running the tool through the ArcGIS Pro geoprocessing dialog.

>| Label | Description | Type |
>| :--- | :--- | :--- |
>| Input Features | Feature that contains records to select. | Feature Layer |
>| Subset Count | Number of records to select. | Long |

### Derived Output

>| Label | Description | Type |
>| :--- | :--- | :--- |
>| Feature With Selection | Input features with selection. | Feature Layer |
>| Count | Number of selected records. | Long |