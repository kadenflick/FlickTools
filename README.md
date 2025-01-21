# FlickTools

FlickTools is ***another*** very cleverly named collection of tools and toolboxes to make life a little easier. These tools are motivated somewhat by laziness, but also by the fact that Pro can't always do what you want it to do.

## Toolboxes

Tools are categorized by theme and organized into toolboxes. Each toolbox aggregates tools that are useful in different scenarios. Tools can be present in multiple toolboxes. For a full list of all tools, see the [Tool List](docs/FT_Tool_List.md).

- **[FT Everyday Toolbox:](docs/ft_everyday_toolbox.md)** Your everyday toolbox. It contains tools that you might use everyday.
- **[FT Fire Toolbox:](docs/ft_everyday_toolbox.md)** Tools to make the life of a GISS mapping fire with the NIFS a little easier.
- **[FT Config Toolbox:](docs/ft_everyday_toolbox.md)** Don't like mucking about in JSON to set configs? Here you go.

## Setup and Use

**Using a Toolbox with ArcGIS Pro**

1. Open the **Add Toolbox** dialog box in an ArcGIS Pro project.
1. Navigate to one of the toolbox folders in the `toolboxes` directory and select the `.pyt` toolbox file.
1. Expand the toolbox in the **Geoprocessing** or **Catalog** panes.
1. Expand a tool category within the toolbox and open a tool. The tool will open in the geoprocessing pane.
1. Set tool parameters and click the **Run** button.

<br>

**Editing Default Tool Values**

1. Add the **[FT Config](docs/FT_Config_Toolbox.md)** toolbox to an ArcGIS Pro project.
1. Open the **Edit Tool Defaults** tool.
1. Change the tool parameters, then click the **Run** button.


## Contact

Feel free to get in touch with any comments, questions, suggestions, or if things start breaking on you. The GitHub repository for this project can be found [here](https://github.com/kadenflick/FlickTools).

---<br>
These tools have only been tested for use with ArcGIS Pro 3.3<br>
This project is based on the [pytframe2](https://github.com/hwelch-fle/pytframe2) framework developed by Hayden Welch.
