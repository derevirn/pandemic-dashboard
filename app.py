import pandas as pd 
import numpy as np
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

data = pd.read_csv("https://raw.githubusercontent.com/datasets/covid-19/master/data/countries-aggregated.csv")
data.replace(0, np.nan, inplace=True)
data.dropna(thresh=3,inplace=True)
data.loc[data["Country"] == 'US', 'Country'] = 'United States of America'

measures = pd.read_excel("data/20200423_acaps_-_covid-19_goverment_measures_dataset_v10.xlsx",
                         sheet_name="Database", parse_dates=True)


measures["COMMENTS"] = measures["COMMENTS"].str.wrap(50)
measures["text"] = "<b>" + measures["DATE_IMPLEMENTED"].dt.strftime("%d-%m-%Y") \
+ "<br>" + measures["MEASURE"] + "</b>" + "<br>" + measures["COMMENTS"] 
measures["text"] = measures["text"].str.replace('\n','<br>', regex=False)


country_list = data["Country"].sort_values().unique()


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css',
                        'https://fonts.googleapis.com/css2?family=Open+Sans']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

app.title = "COVID-19 Pandemic Dashboard"
app.layout = html.Div(children=[
    
    html.H1(children='COVID-19 Pandemic Dashboard',
            style={'background-color': 'rgb(49, 154, 255)',
                   'color': 'white',
                   'border-radius': '18px',
                   'font-size': '4.4rem',
                   'width': '75%'}),
    
    
    html.Div(children=[
    html.P(['''
    Choose the country of your preference to view a graph of the confirmed COVID-19 cases,
    deaths, and/or recovered patients. You can also hover your mouse (or tap) on the
    diamond symbols, to read about the government measures that have been implemented
    in each country. This interactive dashboard has been developed during the
    #HackCoronaGreece hackathon by Giannis Tolios. You can contact me on ''',
    html.A("LinkedIn.", href="https://www.linkedin.com/in/giannis-tolios-0020b067/")],
    style={'width': '90%'}),
    
    
    html.Div(children=[        
            
    dcc.Dropdown(id='select-country',
    style = {'margin-top': '20px'},
    options=[{'label': item, 'value': item} for item in country_list],
    value='Greece'),

    dcc.Checklist(
    id='confirmed',
    style = {'margin-top': '10px'},
    options=[{'label': 'Confirmed Cases', 'value': 'Confirmed Cases'}],
    value=['Confirmed Cases']),
    
    dcc.Checklist(
    id='deaths',
    style = {'margin-top': '5px'},
    options=[{'label': 'Deaths', 'value': 'Deaths'}]),
     
    dcc.Checklist(
    id='recovered',
    style = {'margin-top': '5px'},
    options=[{'label': 'Recovered', 'value': 'Recovered'}]),
    
    dcc.Checklist(
    id='govt_measures',
    style = {'margin-top': '5px'},
    options=[{'label': 'Government Measures', 'value': 'Government Measures'}],
    value=['Government Measures']),

    dcc.RadioItems(
    id='scale',
    style = {'margin-top': '5px', 'padding-bottom': '5px'},
    labelStyle={'display': 'inline-block'},
    options=[{'label': i, 'value': i} for i in ['Linear', 'Logarithmic']],
    value='Linear')],
        
    style={'box-shadow': '#8fc5f9 5px 5px 5px',
           'width':'210px'})], 
    
    style={'columnCount': 2, 'margin-bottom': '40px'}),
    
    
    
    
    dcc.Graph(id='graph'),
    
    html.Footer(["2020 Giannis Tolios"], style={'float': 'right'})
    ],
    
    style={'width': '880px', 'margin': '30px'})


@app.callback(
    Output('graph', 'figure'),
    [Input('select-country', 'value'),
     Input('scale', 'value'),
     Input('confirmed', 'value'),
     Input('deaths', 'value'),
     Input('recovered', 'value'),
     Input('govt_measures', 'value')])
     

def update_graph(country, scale, confirmed, deaths, recovered, govt_measures):
    df = data[data["Country"] == country]
    df_ = measures[measures["COUNTRY"] == country]

    return {
        
        'data':
            [dict(
            x=df['Date'],
            y=df['Confirmed'],
            name='Confirmed Cases',
            visible=True if confirmed else False,
            mode='lines' ),
            
            dict(
            x=df['Date'],
            y=df['Deaths'],
            name='Deaths',
            visible=True if deaths else False,
            mode='lines' ),
            
            dict(
            x=df['Date'],
            y=df['Recovered'],
            visible=True if recovered else False,
            name='Recovered',
            mode='lines' ),
            
            dict(
            x=df_['DATE_IMPLEMENTED'],
            y=np.zeros(len(df_['DATE_IMPLEMENTED'])),
            text=df_['text'],
            visible=True if govt_measures else False,
            name='Government Measures',
            hoverinfo="text",
            mode='markers',
            marker={
                'size': 10,
                'symbol': 'diamond'
                
                })
            
            ],

        'layout':
            dict(
            title="COVID-19 in " + country,
            showlegend=True,
            yaxis={'type': 'linear' if scale == 'Linear' else 'log'},
            margin={'t': 25, 'l': 30})
            
    }
        
        
if __name__ == '__main__':
    app.run_server(debug=False)