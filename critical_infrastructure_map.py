# import packages
import pandas as pd
import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
# from jupyter_dash import JupyterDash
from dash import Dash, html, dcc, Input, Output, State, no_update
import requests
import urllib.parse


# set token, center for plot
mapbox_token = ''
px.set_mapbox_access_token(mapbox_token)

tx_center = dict(lat=31.38, lon=-100.47)

# adjust the plotly dark template to be more in line with Strauss Center colors. This template is close enough that I don't need to construct an entire template.
pio.templates['plotly_dark'].layout.scene.xaxis.gridcolor = '#25412a'
pio.templates['plotly_dark'].layout.scene.yaxis.gridcolor = '#25412a'
colorscale = ["#518e5c",
              "#659a6d",
              "#78a77e",
              "#8bb390",
              "#9ebfa1",
              "#b1ccb4",
              "#c4d9c6",
              "#d8e5d9",
              "#ebf2ec",
              "#ffffff"]
pio.templates['plotly_dark'].layout.colorscale.sequential = list(
    reversed(colorscale))
pio.templates['plotly_dark'].layout.colorway = [
    "#518e5c",
    "#d95f02",
    "#7570b3",
    "#e7298a",
    "#66a61e",
    "#e6ab02",
    "#a6761d",
    "#666666"
]

pio.templates.default = 'plotly_dark'

# read dataset. at this point, I'm just using the emergency services dataset, until I can add additional facility types to it. My plan is to expand this dataset and call it critical infrastructure.
df = pd.read_csv('mysite/data/InfraRiskTX_data.csv')

# data dictionary for overlay
category_dict = {'emergency': 'Emergency Services', 'finance': 'Financial Services', 'electricity': 'Electricity Generation',
                 'energy': 'Energy Production', 'chemical': 'Chemical Production', 'dam': 'Dams'}

chart = px.bar(x=['Economic Impact', 'Physical Impact'], y=[0, 0])
chart.update_xaxes(title='')
chart.update_yaxes(title='Risk Estimate', range=[0, 4])
chart.update_layout(margin=dict(l=58, r=0, t=0, b=0),
                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')

# initialize
app = Dash(__name__)

# build dash layout
app.layout = html.Div([
    dcc.Graph(id='map', clear_on_unhover=True, config={'displaylogo': False, },
              style={'width': '100%', 'height': '100%', 'min-height': 750}
              ),
    dcc.Tooltip(id="graph-tooltip", border_color='#518e5c',
                # including some opacity
                style={'background-color': 'rgba(51, 51, 51, 0.8)'}),
    # main box (top left)
    html.Div([
        # title
        html.H4('Texas Critical Infrastructure Map',
                style={'text-align': 'center', 'font-variant': 'small-caps'}),
        # border line
        html.Hr(
            style={'width': '70%', 'align': 'center'}),
        # Text paragraph for introduction
        html.P("What critical infrastructure do you rely on? When could a failure affect you? Explore the InfraRiskTX dataset with this map to find out."),

        # CI options via radio button
        html.P('Critical Infrastructure Categories:',
               style={'padding-left': 10, 'font-variant': 'small-caps', 'padding-top': 5}),

        # radio buttons HAVE TO COME BACK TO THESE BECAUSE THEY ARE REFERENCED
        dcc.RadioItems({'emergency': 'Emergency Services', 'finance': 'Financial Services', 'electricity': 'Power Grid',
                       'energy': 'Energy Production', 'chemical': 'Chemical Production', 'dam': 'High Risk Dams'}, 'electricity', id='category-selection', inline=False, style={'padding-left': 10, 'display': 'block'}),

        # prompt for address box
        html.P('Center Map on Address . . . ',
               style={'padding-left': 10, 'font-variant': 'small-caps', 'padding-top': 7}),

        # address input field
        html.Div([dcc.Input(id='address',
                            placeholder='Enter an address . . . ',
                            type='text',
                            style={'padding-left': 10}),
                  html.Button('Center', id='btn-update-map-center',
                              style={'padding-left': 30, 'display': 'inline-block'}),
                  ],
                 )
    ],
        style={'position': 'absolute', 'top': 20, 'left': 10, 'width': 325, 'height': 425,
               'background-color': '#333333', 'opacity': 1, 'border-style': 'double', 'border-color': '#305035'
               }
    ),
    # box for  risk chart
    html.Div([
        # title of box
        html.H6('Overall Risk Profile',
                style={'text-align': 'center',
                       'font-variant': 'small-caps', 'font-size': 16}
                ),

        dcc.Graph(id='risk_chart', figure=chart, config={
                  'displayModeBar': False}, style={'height': 210})
    ],
        style={'position': 'absolute', 'top': 470, 'left': 10, 'width': 325, 'height': 250,
               'background-color': '#333333', 'opacity': 1, 'border-style': 'double', 'border-color': '#305035'}),

    # box for facility description
    html.Div([
        # title of box
        html.H6('Facility Description',
                style={'text-align': 'center',
                       'font-variant': 'small-caps', 'font-size': 16}),
        html.Div(id='fac-desc',
                 style={'padding-left': 10, 'padding-right': 10})
    ],
        style={'position': 'absolute', 'top': 390, 'right': 10, 'width': 290, 'height': 330,
               'background-color': '#333333', 'opacity': 1, 'border-style': 'double', 'border-color': '#305035'}
    )

], style={'position': 'absolute', 'width': '100%', 'height': '100%', 'min-width': 1200, 'min-height': 400, 'background-color': '#0d0d0d', 'top': 0, 'left': 0, 'font-family': 'sans-serif', 'color': 'white', 'font-size': 12}
)

# generate map callback. This is the main callback that generates the map. It also also incorporates the address input. When the address is entered, the map is centered on the address and the map is zoomed in.


@app.callback(
    Output('map', 'figure'),
    Input('category-selection', 'value'),
    Input('btn-update-map-center', 'n_clicks'),
    State('address', 'value'),
)
def add_scatter(selector, n_clicks, address):
    df_fig = df.loc[df.CATEGORY == category_dict.get(selector)]
    fig = px.scatter_mapbox(df_fig,
                            lat='LATITUDE',
                            lon='LONGITUDE',
                            color='TYPE',
                            center=tx_center,
                            zoom=5.25,
                            custom_data=['NAME', 'CITY', 'TYPE'],
                            size = 'RAW_IMPACT'
                            )
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0),
                      legend=dict(orientation='v',
                                  title=dict(
                                      text='Facility Sub-Categories (Click to Isolate)',
                                      font=dict(size=13)),
                                  x=.99, y=.95,
                                  xanchor='right',
                                  yanchor='top',
                                  bordercolor='#305035',
                                  borderwidth=2,
                                  bgcolor='#333333',
                                  ),
                      hoverlabel=dict(bgcolor='#333333',
                                      bordercolor='#305035', font_color='white'),
                      )
    fig.update_traces(
        hoverinfo=None, hovertemplate='<b>%{customdata[0]}</b><br>%{customdata[2]}<br>%{customdata[1]}, TX<extra></extra>', 
        marker=dict(opacity=0.6))
    if n_clicks is not None:
        address_to_center = address.encode('utf-8')
        response = requests.get(
            f'https://nominatim.openstreetmap.org/search/{urllib.parse.quote(address_to_center)}?format=json')
        if response.status_code == 200:
            latitude = response.json()[0]["lat"]
            longitude = response.json()[0]["lon"]
            center_loc = {'lat': float(latitude), 'lon': float(longitude)}
            zoom_setting = 12

            # add marker for center_loc
            fig.add_trace(go.Scattermapbox(
                lat=[latitude],
                lon=[longitude],
                mode='markers',
                marker=go.scattermapbox.Marker(
                    symbol='circle',
                    size=10,
                    color='red',
                    opacity=1,
                ),
                hoverinfo='skip',
                name=address
            ))

        else:
            center_loc = tx_center
            zoom_setting = 5.25
        fig.update_layout(mapbox=dict(center=center_loc, zoom=zoom_setting))
    return fig


@app.callback(
    Output('fac-desc', 'children'),
    Input('map', 'hoverData'),
    Input('category-selection', 'value')
)
def update_description(hoverData, overlay):
    if overlay == 'emergency':
        # tooptip for  scatter points
        ftype_dict = {0: 'State Emergency Operations Center',
                      1: 'Local Emergency Operations Center',
                      2: 'FEMA Regional Office'}
        pt = hoverData["points"][0]
        bbox = pt["bbox"]
        num = pt["pointNumber"]
        ftype = ftype_dict.get(pt['curveNumber'])

        df_row = df.loc[df.TYPE == ftype]
        df_row = df_row.iloc[num]
        desc = df_row['desc']
        return desc

    elif overlay == 'finance':
        # tooptip for  scatter points
        ftype_dict = {0: 'Federal Reserve Branch',
                      1: 'Government Finance Facility',
                      2: 'Large Mutual Fund'}
        pt = hoverData["points"][0]
        bbox = pt["bbox"]
        num = pt["pointNumber"]
        ftype = ftype_dict.get(pt['curveNumber'])

        df_row = df.loc[df.TYPE == ftype]
        df_row = df_row.iloc[num]
        desc = df_row['desc']
        return desc

    elif overlay == 'electricity':
        # tooptip for  scatter points
        ftype_dict = {0: 'Powerplant',
                      1: 'Substation',
                      2: 'Nuclear Reactor'}
        pt = hoverData["points"][0]
        bbox = pt["bbox"]
        num = pt["pointNumber"]
        ftype = ftype_dict.get(pt['curveNumber'])

        df_row = df.loc[df.TYPE == ftype]
        df_row = df_row.iloc[num]
        desc = df_row['desc']
        return desc

    elif overlay == 'chemical':
        # tooptip for  scatter points
        ftype_dict = {0: 'Chemicals',
                      1: 'Hazardous Waste',
                      2: 'Other',
                      3: 'Petroelum',
                      4: 'Electric Utilities'}
        pt = hoverData["points"][0]
        bbox = pt["bbox"]
        num = pt["pointNumber"]
        ftype = ftype_dict.get(pt['curveNumber'])

        df_row = df.loc[df.TYPE == ftype]
        df_row = df_row.iloc[num]
        desc = df_row['desc']
        return desc

    elif overlay == 'dams':
        # tooptip for  scatter points
        pt = hoverData["points"][0]
        bbox = pt["bbox"]
        num = pt["pointNumber"]
        df_row = df.loc[df.TYPE == 'Dam']
        df_row = df_row.iloc[num]
        desc = df_row['desc']
        return desc

    else:
        # tooptip for  scatter points
        ftype_dict = {0: 'DOE Petroleum Reserve',
                      1: 'LNG Import/Export Terminal',
                      2: 'Natural Gas Pipeline Compressor Station',
                      3: 'Natural Gas Import/Export Terminal',
                      4: 'Natural Gas Market Hub',
                      5: 'Natural Gas Processing Plant',
                      6: 'Oil Port',
                      7: 'Oil Refinery',
                      8: 'Nuclear Reactor'}
        pt = hoverData["points"][0]
        bbox = pt["bbox"]
        num = pt["pointNumber"]
        ftype = ftype_dict.get(pt['curveNumber'])

        df_row = df.loc[df.TYPE == ftype]
        df_row = df_row.iloc[num]
        desc = df_row['desc']

        return desc


# define callback for risk_chart
@app.callback(
    Output('risk_chart', 'figure'),
    Input('map', 'hoverData'),
    Input('category-selection', 'value')
)
# create bar chart based on hoverdata and facility selected to display values for 'ECONOMIC IMPACT', 'PHYSICAL IMPACT' columns
def update_risk_chart(hoverData, overlay):
    if overlay == 'emergency':
        # tooptip for  scatter points
        ftype_dict = {0: 'State Emergency Operations Center',
                      1: 'Local Emergency Operations Center',
                      2: 'FEMA Regional Office'}
        pt = hoverData["points"][0]
        bbox = pt["bbox"]
        num = pt["pointNumber"]
        ftype = ftype_dict.get(pt['curveNumber'])

        df_row = df.loc[df.TYPE == ftype]
        df_row = df_row.iloc[num]
        econ_impact = df_row['ECONOMIC IMPACT']
        phys_impact = df_row['PHYSICAL IMPACT']
        chart = px.bar(x=['Economic Impact', 'Physical Impact'], y=[
                       econ_impact, phys_impact])
        chart.update_xaxes(title='')
        chart.update_yaxes(title='Risk Estimate', range=[0, 4])
        chart.update_layout(margin=dict(l=58, r=0, t=0, b=0),
                            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        return chart

    elif overlay == 'finance':
        # tooptip for  scatter points
        ftype_dict = {0: 'Federal Reserve Branch',
                      1: 'Government Finance Facility',
                      2: 'Large Mutual Fund'}
        pt = hoverData["points"][0]
        bbox = pt["bbox"]
        num = pt["pointNumber"]
        ftype = ftype_dict.get(pt['curveNumber'])

        df_row = df.loc[df.TYPE == ftype]
        df_row = df_row.iloc[num]
        econ_impact = df_row['ECONOMIC IMPACT']
        phys_impact = df_row['PHYSICAL IMPACT']
        chart = px.bar(x=['Economic Impact', 'Physical Impact'], y=[
                       econ_impact, phys_impact])
        chart.update_xaxes(title='')
        chart.update_yaxes(title='Risk Estimate', range=[0, 4])
        chart.update_layout(margin=dict(l=58, r=0, t=0, b=0),
                            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        return chart

    elif overlay == 'electricity':
        # tooptip for  scatter points
        ftype_dict = {0: 'Powerplant',
                      1: 'Substation',
                      2: 'Nuclear Reactor'}
        pt = hoverData["points"][0]
        bbox = pt["bbox"]
        num = pt["pointNumber"]
        ftype = ftype_dict.get(pt['curveNumber'])

        df_row = df.loc[df.TYPE == ftype]
        df_row = df_row.iloc[num]
        econ_impact = df_row['ECONOMIC IMPACT']
        phys_impact = df_row['PHYSICAL IMPACT']
        chart = px.bar(x=['Economic Impact', 'Physical Impact'], y=[
                       econ_impact, phys_impact])
        chart.update_xaxes(title='')
        chart.update_yaxes(title='Risk Estimate', range=[0, 4])
        chart.update_layout(margin=dict(l=58, r=0, t=0, b=0),
                            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        return chart

    elif overlay == 'chemical':
        # tooptip for  scatter points
        ftype_dict = {0: 'Chemicals',
                      1: 'Hazardous Waste',
                      2: 'Other',
                      3: 'Petroelum',
                      4: 'Electric Utilities'}
        pt = hoverData["points"][0]
        bbox = pt["bbox"]
        num = pt["pointNumber"]
        ftype = ftype_dict.get(pt['curveNumber'])

        df_row = df.loc[df.TYPE == ftype]
        df_row = df_row.iloc[num]
        econ_impact = df_row['ECONOMIC IMPACT']
        phys_impact = df_row['PHYSICAL IMPACT']
        chart = px.bar(x=['Economic Impact', 'Physical Impact'], y=[
                       econ_impact, phys_impact])
        chart.update_xaxes(title='')
        chart.update_yaxes(title='Risk Estimate', range=[0, 4])
        chart.update_layout(margin=dict(l=58, r=0, t=0, b=0),
                            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        return chart

    elif overlay == 'dams':
        # tooptip for  scatter points
        pt = hoverData["points"][0]
        bbox = pt["bbox"]
        num = pt["pointNumber"]
        df_row = df.loc[df.TYPE == 'Dam']
        df_row = df_row.iloc[num]
        econ_impact = df_row['ECONOMIC IMPACT']
        phys_impact = df_row['PHYSICAL IMPACT']
        chart = px.bar(x=['Economic Impact', 'Physical Impact'], y=[
                       econ_impact, phys_impact])
        chart.update_xaxes(title='')
        chart.update_yaxes(title='Risk Estimate', range=[0, 4])
        chart.update_layout(margin=dict(l=58, r=0, t=0, b=0),
                            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        return chart

    else:
        # tooptip for  scatter points
        ftype_dict = {0: 'DOE Petroleum Reserve',
                      1: 'LNG Import/Export Terminal',
                      2: 'Natural Gas Pipeline Compressor Station',
                      3: 'Natural Gas Import/Export Terminal',
                      4: 'Natural Gas Market Hub',
                      5: 'Natural Gas Processing Plant',
                      6: 'Oil Port',
                      7: 'Oil Refinery',
                      8: 'Nuclear Reactor'}
        pt = hoverData["points"][0]
        bbox = pt["bbox"]
        num = pt["pointNumber"]
        ftype = ftype_dict.get(pt['curveNumber'])

        df_row = df.loc[df.TYPE == ftype]
        df_row = df_row.iloc[num]
        econ_impact = df_row['ECONOMIC IMPACT']
        phys_impact = df_row['PHYSICAL IMPACT']
        chart = px.bar(x=['Economic Impact', 'Physical Impact'], y=[
                       econ_impact, phys_impact])
        chart.update_xaxes(title='')
        chart.update_yaxes(title='Risk Estimate', range=[0, 4])
        chart.update_layout(margin=dict(l=58, r=0, t=0, b=0),
                            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        return chart


# close
if __name__ == '__main__':
    app.run_server(debug=True)
