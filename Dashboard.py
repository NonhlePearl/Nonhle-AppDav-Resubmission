import requests
import pandas as pd
import pickle
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go

# Calls API to get windfarm meterological data
def wind_predict():
    url2 = 'http://www.7timer.info/bin/api.pl?lon=8.591&lat=53.562&product=meteo&output=json'
    Wind_Plant = requests.get(url2).json()
    date_data = requests.get(url).json()
    wind_speed = []
    wind_direction = []
    date = []
    for i in range(7):
        wspeed = Wind_Plant['dataseries'][i]['wind_profile'][0]['speed']
        wdirection = Wind_Plant['dataseries'][i]['wind_profile'][0]['direction']
        dt = date_data['dataseries'][i]['date']
        wind_speed.append(wspeed)
        wind_direction.append(wdirection)
        date.append(dt)
#Converting the speed values by using average values as specified in the documentation info of the api as per interval to suitable values for model
    speed_value ={'1': 0.3, '2': 1.83, '3':5.7, '4':9.4, '5':14, '6':20.85, '7':28.55, '8':34.65, '9':39.05, '10':43.8, '11':48.55, '12':53.4, '13':55.9}
    wind_speed = []
    wind_direction = []
    for i in range(7):
        s = Wind_Plant['dataseries'][i]['wind_profile'][0]['speed']
        wspeed = speed_value[str(s)] #Use created dictionary labeled speed_value
        wdirection = Wind_Plant['dataseries'][i]['wind_profile'][0]['direction']
        wind_speed.append(wspeed)
        wind_direction.append(wdirection)
#Creating a data frame
    df = pd.DataFrame([wind_speed, wind_direction]).transpose()
    df.columns = ['wind_speed', 'wind_direction']
    import pickle
    wind_model = pickle.load(open('wind_model.sav','rb'))# loading the wind model
    wind_plant_power = wind_model.predict(df.values)# predicted values
    return wind_plant_power, date

def solar_predict():
    # Getting the weather condition data and parameters infor:
    url = 'http://www.7timer.info/bin/api.pl?lon=141.988&lat=-20.219&product=meteo&output=json'
    Solar = requests.get(url).json()

    url1 = 'http://www.7timer.info/bin/api.pl?lon=141.988&lat=-20.219&product=meteo&output=json'
    Solar_Plant = requests.get(url1).json()

    data_size = len(Solar["dataseries"])
    date = []
    Temp_Hi = []
    Temp_Low = []
    for i in range(data_size):
        sdate = Solar['dataseries'][i]['date']
        smax = Solar['dataseries'][i]['temp2m']['max']
        smin = Solar['dataseries'][i]['temp2m']['min']
        date.append(sdate)
        Temp_Hi.append(smax)
        Temp_Low.append(smin)

    Cloud_Cover_Percentage =[]
    for i in range(7):
        cloud = Solar_Plant['dataseries'][i]['cloudcover']
        Cloud_Cover_Percentage.append(cloud)
    data = pd.DataFrame([date,Temp_Hi, Temp_Low, Cloud_Cover_Percentage]).transpose()

    data['Temp Hi']= (data[1]*9/5) + 32 #Converting maximum temperatures to Frahenhei
    data['Temp Low']= (data[2]*9/5) + 32 #Converting minimun temperatues to Frahenhei
    data["Cloud Cover Percentage"] = data[3]
    data.drop([0,1,2,3], inplace =True, axis = 1)# Dropping unnamed columns
    import pickle
    solar_model = pickle.load(open('solar_model.sav', 'rb'))
    solar_plant_power = solar_model.predict(data.values) # The predicted values
    return solar_plant_power, date


df_solar = pd.DataFrame(solar_predict()).transpose()
df_solar.columns = ['Solar Predictions', 'Date']
df_solar['Date'] = pd.to_datetime(df['Date'].astype(str), format='%Y%m%d')
df_solar.set_index('Date', inplace = True)

df_wind = pd.DataFrame(wind_predict()).transpose()
df_wind.columns = ['Wind Predictions', 'Date']
df_wind['Date'] = pd.to_datetime(df_1['Date'].astype(str), format='%Y%m%d')
df_wind.set_index('Date', inplace = True)


def get_dash(server):
    external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
    app = dash.Dash(__name__,
                    server=server,
                    routes_pathname_prefix='/dashapp/',
                    external_stylesheets=external_stylesheets
                    )
    trace1 = go.Bar(x=df.index, y = df['Solar Predictions'],
              name = 'Solar Predictions')
    layout1 = go.Layout(yaxis = {'title': 'MW'})

    trace2 = go.Bar(x=df_1.index, y = df_1['Wind Predictions'],
              name = 'Wind Predictions')
    layout2 = go.Layout(yaxis = {'title': 'MW'})
    # df = get_data()

    styles = get_styles()

    # fig = px.bar(df, x="Fruit", y="Amount", color="City", barmode="group")

    app.layout = html.Div([
                        html.Div([
                        # html.H6("Change the value in the text box to see callbacks in action!"),
                        html.A("Go to Home Page", href="/", style=styles["button_styles"]),
                        html.Div("Solar Farm Predictions", id='solar',
                                 style=styles["text_styles"]),
                        html.Div(
                            dcc.Graph(
                                id='solar-predict',
                                figure = {'data': [trace1],
                                          'layout':layout1}
                                    ),
                                style=styles["fig_style"]
                                )
                               ]),
                        html.Div([
                        html.Div("Wind Farm Predictions", id='wind',
                                 style=styles["text_styles"]),
                        html.Div(
                            dcc.Graph(
                                id='wind-predict',
                                figure = {'data': [trace2],
                                          'layout':layout2}
                                    ),
                                style=styles["fig_style"]
                                )
                               ]),
                        ])

    return app


# def get_data():
#     df = pd.DataFrame({
#             "Fruit": ["Apples", "Oranges", "Bananas", "Apples", "Oranges", "Bananas"],
#             "Amount": [4, 1, 2, 2, 4, 5],
#             "City": ["SF", "SF", "SF", "Montreal", "Montreal", "Montreal"]
#         })
#     return df


def get_styles():
    """
    Very good for making the thing beautiful.
    """
    base_styles = {
        "text-align": "center",
        "border": "1px solid #ddd",
        "padding": "7px",
        "border-radius": "2px",
    }
    text_styles = {
        "background-color": "#eee",
        "margin": "auto",
        "width": "50%"
    }
    text_styles.update(base_styles)

    button_styles = {
        "text-decoration": "none",
    }
    button_styles.update(base_styles)

    fig_style = {
        "padding": "10px",
        "width": "80%",
        "margin": "auto",
        "margin-top": "5px"
    }
    fig_style.update(base_styles)
    return {
        "text_styles" : text_styles,
        "base_styles" : base_styles,
        "button_styles" : button_styles,
        "fig_style": fig_style,
    }
