# FlickTools

FlickTools is ***another*** very cleverly named collection of tools and toolboxes to make the life of a GIS professional a little easier. These tools are motivated somewhat by laziness, but also by the fact that Pro can't always do what you want it to.

## Toolboxes

Each toolbox contains tools that are useful in different scenarios. Within each toolbox, tools are categorized and grouped by theme. For a full list of all tools, see the **[Tool List](docs/Tool_List.md)**.

- **[FT Everyday Toolbox:](docs/toolbox_FT_Everyday.md)** Your everyday toolbox. It contains tools that you might use everyday.
- **[FT Fire Toolbox:](docs/toolbox_FT_Fire.md)** Tools to make the life of a GISS mapping fire with the NIFS a little easier.
- **[FT Config Toolbox:](docs/toolbox_FT_Config.md)** Don't like mucking about in JSON to set configs? Here ya go.

## Setup and Use

### Downloading the Latest Version of FlickTools

There are several ways to download FlickTools to your computer. The most common way is to clone the GitHub repository as you would any other. Staying current with the `main` branch will make sure you always have the latest updates. Instructions for cloning a GitHub repository can be found [here](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository). If you don't feel like cloning the repository, the FlickTools source code for every version can be downloaded from GitHub. Instructions for that are below. Using this method requires manual updates to the toolbox, which might break the links to the toolbox in your ArcGIS Pro projects if not done carefully.

If you prefer not to clone the repository, use these instructions to download the latest version:

1. Download the `.zip` file for the last version of FlickTools from the [**Releases**](https://github.com/kadenflick/FlickTools/releases) section of the GitHub repository.
1. Unpack the `.zip` file to an appropriate location on your computer.

### Using a Toolbox with ArcGIS Pro

Regardless of the method used to download the toolbox, adding the toolbox files to a project and running the tools within it are the same:

1. Open the **Add Toolbox** dialog box in an ArcGIS Pro project.
1. Navigate to one of the toolbox folders in the `toolboxes` directory and select the `.pyt` toolbox file.
1. Expand the toolbox in the **Geoprocessing** or **Catalog** panes.
1. Expand a tool category within the toolbox and open a tool. The tool will open in the geoprocessing pane.
1. Set tool parameters and click the **Run** button.

### Editing Default Tool Values

FlickTools uses a configuration file to store defualt tool settings. This means that those settings can be changed to personalize the toolbox to an individual user. You're more than welcome to muck around in the JSON, but I prefer a GUI:

1. Add the **[FT Config](docs/toolbox_FT_Config.md)** toolbox to an ArcGIS Pro project.
1. Open the **Edit Tool Defaults** tool.
1. Change the tool parameters, then click the **Run** button.

## Contact

Feel free to get in touch with any comments, questions, suggestions, or if things start breaking on you. The GitHub repository for this project can be found [here](https://github.com/kadenflick/FlickTools).

---<br>
These tools have only been tested for use with ArcGIS Pro 3.3<br>
This project is based on the [pytframe2](https://github.com/hwelch-fle/pytframe2) framework developed by Hayden Welch.
