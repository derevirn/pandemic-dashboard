import pandas as pd 
import numpy as np
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output


data = pd.read_csv("https://s3.amazonaws.com/rawstore.datahub.io/739d58f443412d5778140f6c4a28f7c5.csv")
data.replace(0, np.nan, inplace=True)
data.dropna(thresh=3,inplace=True)

measures = pd.read_excel("data/acaps-covid-19-goverment-measures-dataset-v6.xlsx",
                         sheet_name="Database", parse_dates=True)

measures["text"] = measures["DATE_IMPLEMENTED"].dt.strftime("%d-%m-%Y") + ": \n" \
+ measures["MEASURE"] + "\n" + measures["COMMENTS"] 

measures["text"] = measures["text"].str.wrap(30)
measures["text"] = measures["text"].str.replace('\n','<br>', regex=False)


measures
country_list = data["Country"].sort_values().unique()


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

app.title = "COVID-19 Pandemic Dashboard"
app.layout = html.Div(children=[
    
    html.H1(children='COVID-19 Pandemic Dashboard'),
    html.P(['''
    Choose a country to view graphs of the confirmed cases, deaths, or recovered patients. 
    You can click/tap on the data points for more details. This interactive
    dashboard was developed during the #HackCoronaGreece hackathon, by Giannis Tolios. You can contact me 
    on ''',
    html.A("LinkedIn.", href="https://www.linkedin.com/in/giannis-tolios-0020b067/")]),
    
    
    dcc.Dropdown(id='select-country',
    style = {'margin-top': '30px', 'width': '300px'},
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

    
    dcc.RadioItems(
    id='scale',
    style = {'margin-top': '10px',},
    labelStyle={'display': 'inline-block'},
    options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
    value='Linear'),
    
    
    dcc.Graph(id='graph')],
    
    style={'width': '900px', 'margin': '30px'})


@app.callback(
    Output('graph', 'figure'),
    [Input('select-country', 'value'),
     Input('scale', 'value'),
     Input('confirmed', 'value'),
     Input('deaths', 'value'),
     Input('recovered', 'value')])
     

def update_graph(country, scale, confirmed, deaths, recovered):
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
            name='Govt Measures',
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
            xaxis={'title': 'date'},
            yaxis={'type': 'linear' if scale == 'Linear' else 'log'},
            margin={'t': 25})
            
    }
        
        
if __name__ == '__main__':
    app.run_server(debug=True)