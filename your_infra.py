# %%
import plotly.io as pio
from dash import Dash, html, dcc, Input, Output, State, no_update, dash_table
import pandas as pd
import openpyxl


df = pd.read_csv('InfraRiskTX_data.csv')

df = df[['NAME', 'TYPE', 'CATEGORY', 'ADDRESS', 'CITY',
         'ZIP', 'COUNTY', 'STRATEGIC VALUE', 'SYSTEMIC IMPACT', 'ECONOMIC IMPACT',
         'PHYSICAL IMPACT', 'PHYSICAL IMPACT RADIUS (mi)',
         'ZIPS AFFECTED', 'POPULATION AFFECTED',
         'desc']]

df.columns = ['Facility Name', 'Type', 'Category', 'Address', 'City', 'ZIP Code', 'County',
              'Strategic Value?', 'Systemic Impact?', 'Economic Impact Score',
              'Physical Impact Score', 'Physical Impact Radius (mi)', 'Zip Codes Affected',
              'Population Affected', 'Description']
# Define values for numerical columns
df['Strategic Value?'] = df['Strategic Value?'].map({'Yes': 1, 'No': 0})
df['Systemic Impact?'] = df['Systemic Impact?'].map({'Yes': 1, 'No': 0})

# Define values for categorical columns
economics = {0: "No Impact", 1: "Local Impact",
             2: "Regional Impact", 3: "National Impact", 4: "Global Impact"}
physical = {0: "No Impact", 1: "Minor Impact",
            2: "Substantial Impact", 3: "Substantial and Persistent Impact"}

# overwrite values
df['Economic Impact Score'] = df['Economic Impact Score'].map(economics)
df['Physical Impact Score'] = df['Physical Impact Score'].map(physical)


# Initialize the Dash app
app = Dash(__name__)

# Define the layout
app.layout = html.Div([
    html.H1("Your Infrastructure"),
    html.P("Use this tool to find infrastructure near you. Search by city, county, or zip code. Download for more information."),
    html.Div([
        html.Div([
            dcc.Input(id='input-city', type='text',
                      placeholder='Enter city...'),
        ], style={'marginRight': '10px'}),
        html.Div([
            dcc.Input(id='input-county', type='text',
                      placeholder='Enter county...'),
        ], style={'marginRight': '10px'}),
        html.Div([
            dcc.Input(id='input-zip', type='text',
                      placeholder='Enter zip code...'),
        ], style={'marginRight': '10px'}),
        html.Button('Search', id='search-button', n_clicks=0,
                    style={'marginBottom': 10, 'marginTop': 10}),
        html.Div([html.Button("Download CSV", id="btn_csv"),
                  dcc.Download(id="download-dataframe-csv")
                  ]),
        html.Div([html.Button("Download Excel", id="btn_xlsx"),
                  dcc.Download(id="download-dataframe-xlsx")
                  ]),
    ], style={'display': 'flex', 'alignItems': 'center'}),
    html.Div(id='output-table', className='custom-table')
])

# Callback to generate the table based on user input


@app.callback(
    Output('output-table', 'children'),
    [Input('search-button', 'n_clicks')],
    [State('input-city', 'value'),
     State('input-county', 'value'),
     State('input-zip', 'value')]
)
def generate_table(n_clicks, city, county, zip_code):
    if n_clicks > 0:
        # Filter the data based on user input
        # Replace missing values with an empty string
        filtered_df = df.fillna('')
        if city:
            filtered_df = filtered_df[filtered_df['City'].str.contains(
                city, case=False, na=False)]
        if county:
            filtered_df = filtered_df[filtered_df['County'].str.contains(
                county, case=False, na=False)]
        if zip_code:
            filtered_df = filtered_df[filtered_df['ZIP Code'].astype(
                str).str.contains(zip_code)]

        # drop zip codes affected column
        filtered_df = filtered_df.drop(columns=['Zip Codes Affected'])

        # Create the table
        table = html.Table(
            [html.Tr([html.Th(col) for col in filtered_df.columns])] +
            [html.Tr([html.Td(filtered_df.iloc[i][col]) for col in filtered_df.columns])
             for i in range(len(filtered_df))],
            className='custom-table',
        )
        return table
    else:
        return ''


@app.callback(
    Output("download-dataframe-csv", "data"),
    Input("btn_csv", "n_clicks"),
    [State('input-city', 'value'),
     State('input-county', 'value'),
     State('input-zip', 'value')],
    prevent_initial_call=True,
)
def func(n_clicks,  city, county, zip_code):
    # Filter the data based on the same criteria as the table
    filtered_df = df.fillna('')

    if city:
        filtered_df = filtered_df[filtered_df['City'].str.contains(
            city, case=False, na=False)]
    if county:
        filtered_df = filtered_df[filtered_df['County'].str.contains(
            county, case=False, na=False)]
    if zip_code:
        filtered_df = filtered_df[filtered_df['ZIP Code'].astype(
            str).str.contains(zip_code)]

    return dcc.send_data_frame(filtered_df.to_csv, "your_infrastructure.csv")

@app.callback(
    Output("download-dataframe-xlsx", "data"),
    Input("btn_xlsx", "n_clicks"),
    [State('input-city', 'value'),
     State('input-county', 'value'),
     State('input-zip', 'value')],
    prevent_initial_call=True,
)
def func(n_clicks,  city, county, zip_code):
    # Filter the data based on the same criteria as the table
    filtered_df = df.fillna('')

    if city:
        filtered_df = filtered_df[filtered_df['City'].str.contains(
            city, case=False, na=False)]
    if county:
        filtered_df = filtered_df[filtered_df['County'].str.contains(
            county, case=False, na=False)]
    if zip_code:
        filtered_df = filtered_df[filtered_df['ZIP Code'].astype(
            str).str.contains(zip_code)]

    return dcc.send_data_frame(filtered_df.to_excel, "your_infrastructure.xlsx", sheet_name="Infrastructure")


if __name__ == '__main__':
    app.run_server(debug=True)



