import numpy as np
import pandas as pd
import plotly.express as px
import dash  # (version 1.8.0)
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import base64
import os


df = pd.read_csv('df')


external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
app = dash.Dash( __name__ )
blackbold={'color':'black', 'font-weight': 'bold'}
rangeslider_marks = {0:'0 Miles', 3:'3 Miles', 6:'6 Miles', 9:'9 Miles', 12:'12 Miles'}

app.layout = html.Div(children=[
    # Full-height container to allow vertical centering
    html.Div(style={'position': 'fixed', 'top': '0', 'right': '0', 'margin-right': '10px'},
        children=[
            html.Img(src='/assets/logo.png', style={'max-height': '100px', 'margin-right': '10px'})
        ]),
    # Container for checklists
    html.Div([
        # Repair Issue Checklist
        html.Div([ 
            html.Label(['Repair Issue: '], style=blackbold),
            dcc.Checklist(id='problem',
                          options=[{'label': str(b), 'value': b} for b in sorted(df['Problem'].unique())],
                          value=['clutch replacement'],
                          )
        ], style={'margin-right': '20px', 'font-family':'arial'}),  # Spacing between checklists

        # City Checklist
        html.Div([
            html.Label(['City: '], style=blackbold),
            dcc.Checklist(id='city',
                          options=[{'label': str(b), 'value': b} for b in sorted(df['city'].unique())],
                          value=['Bristol']
                          )
        ]),
    ], style={'display': 'flex', 'flex-direction': 'row', 'align-items': 'flex-start', 'font-family':'arial'}),

    # Distance from Halfords
    html.Div([
        html.Label(["Distance from Halfords:"], style={'font-weight': 'bold', 'margin-left': '5mm'}),
        dcc.RangeSlider(0, 15, value=[0, 6], marks=rangeslider_marks, dots=False,
                        updatemode='drag', tooltip={"placement": "top", "always_visible": False},
                        persistence=True, persistence_type='session', id="my-rangeslider")
    ], style={'margin-top': '20px', 'margin-left': '-20px', 'font-family':'arial'}), 

    # Earliest Availability
    html.Div(children=[
        html.Div([
            html.Div([
                html.Label(['Earliest Availability:'], style={
                    'font-weight': 'bold',
                    'margin-right': '10px',  # Space between label and Pre content
                }),
                html.Pre(id='avail', children=[], 
                         style={
                             'display': 'inline-block', 
                             'font-weight': 'bold',
                             'font-size': '16px',
                             'margin': '0',
                              'font-family':'arial',
                             'vertical-align': 'bottom',
                         }),
            ], style={
                'display': 'flex', 
                'align-items': 'center', 
                'margin-left': '-2px',  # Adjust positioning
                'margin-top': '15px',
                 'font-family':'arial'
            }),
        ], className='two columns'),
    ]),

    # Graph
    html.Div([
        dcc.Graph(id='the_graph', style={'height': '600px', 'width': '1200px', 'width': '100%', 'display': 'flex', 'justify-content': 'center'})
    ]),
], style={'backgroundColor': '#dedede', 'minHeight': '100vh', 'width': '100vw', 'overflow': 'hidden'})  
@app.callback(
    Output( 'the_graph', 'figure' ),
    [Input( 'problem', 'value' ),
     Input( 'city', 'value' ),
     Input( 'my-rangeslider', 'value' ),]
)
def update_graph(problem, city, distance):
    rest_df = df[df['Shops']!='Halfords Autocentre']
    rest_df = rest_df[(rest_df['city'].isin(city)) & (rest_df['Problem'].isin(problem))]
    rest_df = rest_df[(rest_df['Distance from Halfords']>=distance[0]) & (rest_df['Distance from Halfords']<=distance[1]) ]

    latitude_mean = rest_df["latitude"].median()
    longitude_mean = rest_df["longitude"].median() 
    token = 'pk.eyJ1IjoiZ3JpZ2FzIiwiYSI6ImNsZGsxcXBrZTA5Z20zcnFtN3N1NXN5ZXMifQ.52mus-gyBTsNDoI32_8pkQ'

    fig= go.Figure(go.Scattermapbox(lat=rest_df['latitude'],
                             lon=rest_df['longitude'],
                             mode='text+markers',
                             opacity = 1,
                             text = rest_df["Prices"],      
                             textposition='top center',
                             marker_size=15,
                             marker = {'size': 20, 'symbol': "circle"},
                             textfont=dict(color='black', size=16),
                             hovertext = rest_df["Shops"],
                             hoverinfo='text',
                             customdata=rest_df['earliest_avail']))

        # Filter data for specific shop
    halfords_df = df[df['Shops'] == 'Halfords Autocentre']

    # Create scattermapbox trace for specific shop with red marker
    fig.add_trace(go.Scattermapbox(
        lat=halfords_df['latitude'],
        lon=halfords_df['longitude'],
        mode='text+markers',
        opacity=1,
        text='Halfords Autocentre',
        textposition='top center',
        marker_size=15,
        marker={'size': 20, 'symbol': 'car', 'color': 'red'},
        textfont=dict(color='red',  size=15),
        hovertext=halfords_df['Shops'],
        hoverinfo='text',
    ))

    fig.update_layout(mapbox_style="streets", mapbox_accesstoken=token,showlegend=False,
                    mapbox_center={"lat": latitude_mean, "lon": longitude_mean},
        mapbox=dict(zoom=10),
        hovermode="closest",
        margin={"r": 0, "t": 0, "l": 0, "b": 0}
    )

    return fig

# second callback 
@app.callback(
    Output('avail', 'children'),
    [Input('the_graph', 'clickData')])
def display_click_data(clickData):
    if clickData is None:
        return 'Click on any Garage'
    else:
        # print (clickData)
        the_link=clickData['points'][0]['customdata']
        if the_link is None:
            return 'No availability'
        else:
            return the_link

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8050))  # Use PORT env var if available, else default to 8050
    app.run_server(debug=False, host='0.0.0.0', port=port)