# Import required libraries
import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                # dcc.Dropdown(id='site-dropdown',...)
                                html.Div([
                                    dcc.Dropdown(
                                        id='site-dropdown',
                                        options=[
                                            {'label':'Total','value':'Total'},
                                            {'label':'CCAFS LC-40' , 'value':'CCAFS LC-40'},
                                            {'label':'CCAFS SLC-40' , 'value':'CCAFS SLC-40'},
                                            {'label':'KSC LC-39A' , 'value':'KSC LC-39A'},
                                            {'label':'VAFB SLC-4E' , 'value':'VAFB SLC-4E'}
                                        ],
                                        placeholder='Select Launch Site',
                                        value='Total',
                                        style={'width':'80%', 'padding':'3px', 'font-size':'20px', 'text-align-last':'center'}
                                    )
                                ], style={'margin':'70px'}),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                #dcc.RangeSlider(id='payload-slider',...)
                                html.Div([
                                    dcc.RangeSlider(id='payload-slider', min=0, max=9600, step=1, value=[0, 9600],
                                    marks={i: '{}'.format(i) for i in range(9600)}, updatemode='drag'
,
)
                                ],style={'margin':'auto'}),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])


def get_successSites(data:pd.DataFrame()):
    d = data.groupby(['Launch Site'], as_index=False)['class'].value_counts()
    return d.loc[d['class'] == 1, ['Launch Site', 'count']]
# get_successSites(spacex_df)


def get_site_info(data:pd.DataFrame(), col):
    return data.loc[data['Launch Site'] == col, ['class']].value_counts().to_frame().reset_index()
# get_site_info(spacex_df, 'KSC LC-39A')

def getScatterTotal(data:pd.DataFrame(), slider):
    d = data[['Payload Mass (kg)', 'class', 'Booster Version Category']]
    return d[(d['Payload Mass (kg)'] >= slider[0]) & (d['Payload Mass (kg)'] <= slider[1])]
# getScatterTotal(spacex_df, [0, 2000])


def getScatterSite(data:pd.DataFrame(),site, slider):
    d = data[['Payload Mass (kg)','Launch Site', 'class', 'Booster Version Category']]
    return d[(d['Payload Mass (kg)'] >= slider[0]) & (d['Payload Mass (kg)'] <= slider[1]) & (d['Launch Site'] == site)]
# getScatterSite(spacex_df,'KSC LC-39A', [0, 9600])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(Output('success-pie-chart', 'figure'),
             Input('site-dropdown', 'value'))
def get_graph(site):
    if str(site)=='Total':
        successSites = get_successSites(spacex_df)
        successPie = px.pie(successSites, names='Launch Site', values='count')
        return successPie
    else:
        s = str(site)
        siteInfo = get_site_info(spacex_df, s)
        sitePie = px.pie(siteInfo, names='class', values=0)
        return sitePie
# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output('success-payload-scatter-chart', 'figure'),
                [Input('payload-slider', 'value'),
                Input('site-dropdown', 'value')],
                State('success-payload-scatter-chart', 'figure'))
def get_graph2(slider, site, state):
    if site =='Total':
        siteInfo = getScatterTotal(spacex_df, slider)
        return px.scatter(siteInfo, x='Payload Mass (kg)', y='class', color='Booster Version Category')
    else:
        siteInfo = getScatterSite(spacex_df,site, slider)
        return px.scatter(siteInfo, x='Payload Mass (kg)', y='class', color='Booster Version Category')



# Run the app
if __name__ == '__main__':
    app.run_server(host='localhost', port=8080, debug=True)
