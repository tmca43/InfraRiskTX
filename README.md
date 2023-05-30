# InfraRiskTX: Mapping Critical Infrastructure Risks for Texans

 InfraRiskTX critical infrastruture assessment project. The purpose of this project is to help Texans understand their personal critical infrastructure risks. This project is made possible by the generous support of the Strauss Center for International Security and Law at the University of Texas at Austin.

 This project required aggregating a large dataset of critical infrastructure in the state and assessing the risk profile for each piece of infrastructure. Although the dataset is not exhaustive, it illustrates some of the key vulnerabiliies facing Texans.

 Much of the value from this project comes from visualizing and interacting with the data. To this end, I have created a website where Texans can use a suite of tools that will help them understand their personal risk profile. The webiste also features a few posts about specific findings that this dataset exposed. Please visit [InfraRiskTX](https://www.infrarisktx.org) for more information.

## Repository Contents

| File      | Format | Description |
| ----------- | ----------- |----------- |
| InfraRiskTX_data      | Comma Separated Values | Aggregated dataset of high risk critical infrastructure in Texas.
|critical_infrastructure_map|Python Script|Plotly Dash App to visualize all critical infrastructure in the state. Replication requires Mapbox token and CSS stylesheet. Viewable [here](https://infrarisktx.pythonanywhere.com/).
|your_infrastructure|Python Script|Plotly Dash App to generate a spreadsheet based off user values. Viewable [here](https://yourinfrastructure-infrarisktx.pythonanywhere.com/).

Special thanks to the [Strauss Center for International Security and Law at the University of Texas at Austin](https://www.strausscenter.org/) and the [Jon and Rebecca Brumley Fellowship](https://www.strausscenter.org/brumley-fellows/). 

Thanks also to Strauss Fellow [Bryan Jones](https://www.strausscenter.org/person/bryan-jones/) for his support and guidance on this project.