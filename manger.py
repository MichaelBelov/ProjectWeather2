from dash import Dash, html, dcc, Output, Input, State, ALL
import plotly.express as px
import dash_bootstrap_components as dbc
import pandas as pd
from wth_app import get_location_key_by_name, get_forecast, get_cur_conditions

APIKEY = '2RabSK7iNucLunigoc67jMmvIILMg7qj'

app = Dash(__name__, external_stylesheets=[dbc.themes.ZEPHYR])


temp_graph = dcc.Graph(
    id="temp-graph", style={'display': 'inline-block', 'width': '48%'}
)

hum_graph = dcc.Graph(
    id="humidity-graph", style={'display': 'inline-block', 'width': '48%'})

wind_graph = dcc.Graph(
    id="wind-graph", style={'display': 'inline-block', 'width': '48%'})


rain_graph = dcc.Graph(
    id="rain-graph", style={'display': 'inline-block', 'width': '48%'})

app.layout = html.Div(
    children=[
        html.H1("Weather prognosis between cities", style={'textAlign': 'center'}),

        dbc.Col(children=[
            html.Div([
                html.Label("First city (please? print on Russian):", style={"margin-right": "20px"}),
                dcc.Input(id="namecity_1", type="text", placeholder="Moscow"),
            ], style={'margin-bottom': '20px', "textAlign" : "center"}),

            html.Div(id='intermediate-stops-container', style={"textAlign" : "center"}),

            html.Div([
                html.Label("Second city:", style={"margin-right": "20px"}),
                dcc.Input(id="namecity_2", type="text", placeholder="Kazan"),
            ], style={'margin-bottom': '20px', "textAlign" : "center"}),


            html.Div([
                html.Button('Add a stop', id='add-stop', n_clicks=0, style={"textAlign": "center"}),

            ], style={'margin-bottom': '20px', "textAlign": "center"}),


            html.Div(dcc.Slider(
                id='days-slider', min=1, max=5, step=1, value=5,
                marks={i: str(i) for i in range(1, 11)},
                tooltip={"placement": "bottom", "always_visible": True},
                    ),
                style={'width': '25%', 'margin': 'auto'}
            ),

            html.Div(html.Button('Compare', id='submit-val', n_clicks=0),
                     style={'textAlign': 'center', 'margin-top': '20px'}),

        ]),

        # Output area for comparison
        html.H3(id="weather-output", style={'textAlign': 'center'}),

        # Graph area for comparison
        html.Div([
            temp_graph,
            hum_graph,
        ], style={'display': 'flex', 'justify-content': 'space-between', 'margin-top': '20px'}),

        html.Div([
            wind_graph,
            rain_graph,
        ], style={'display': 'flex', 'justify-content': 'space-between', 'margin-top': '20px'}),

        html.I('Diagrams for comparison',
               style={'textAlign': 'center', 'margin-top': '20px'}),

        html.H3('Weather prognosis', style={'textAlign': 'center'}),

        # Графики прогноза по дням для всех городов
        html.Div(id='forecast-graphs-container', style={'margin-top': '40px'}),

        dcc.Store(id='num-stops', data=0)
    ]
)


@app.callback([
    Output('intermediate-stops-container', 'children'),
    Output('num-stops', 'data')],
    Input('add-stop', 'n_clicks'),
    State('num-stops', 'data')
)
def add_stop_fields(n_clicks, num_stops):
    if n_clicks == 0:
        return None, 0
    stops = num_stops + 1
    stop_fields = [
        html.Div([
            html.Label(f"Stop {i + 1}:", style={"margin-right": "10px"}),
            dcc.Input(id={'type': 'namecity', 'index': i}, type="text", placeholder=f"City {i + 1}"),
        ], style={'margin-bottom': '20px'}) for i in range(stops)
    ]
    return stop_fields, stops


@app.callback(
    [
        Output('weather-output', 'children'),
        Output('temp-graph', 'figure'),
        Output('humidity-graph', 'figure'),
        Output('wind-graph', 'figure'),
        Output('rain-graph', 'figure'),
        Output('forecast-graphs-container', 'children'),
    ],
    Input('submit-val', 'n_clicks'),
    [
        State('namecity_1', 'value'),
        State('namecity_2', 'value'),
        State('days-slider', 'value'),
        State({'type': 'namecity', 'index': ALL}, 'value'),
        State({'type': 'mode', 'index': ALL}, 'value'),
    ]
)
def update_output(n_clicks, city_name_1, city_name_2, days_c, intermediate_cities, intermediate_modes, api_key=APIKEY):
    if n_clicks == 0 or not api_key:
        return "", {}, {}, {}, {}, ""

    # Collect all cities and modes
    all_cities = [city_name_1] + intermediate_cities + [city_name_2]
    weather_data = []

    for city in all_cities:
        try:
            location_key = get_location_key_by_name(api_key, city)
            conditions = get_cur_conditions(api_key, location_key)
            weather_data.append({
                'City': city,
                'Temperature': conditions['temperature'],
                'Humidity': conditions['humidity'],
                'Wind Speed': conditions['wind_speed'],
                'Rain Probability': conditions['precipitation_probability']
            })
        except Exception as e:
            return f"Error for city {city}: {str(e)}", {}, {}, {}, {}, ""

    df = pd.DataFrame(weather_data)
    temp_fig = px.bar(df, x='City', y='Temperature', title="Temperature (°C)",
                      labels={"City": "Cities", 'temperature': 'Год'})

    humidity_fig = px.bar(df, x='City', y='Humidity', title="Humidity (%)",
                          labels={"City": "Cities", "Humidity": "Humiditi percent"})
    wind_fig = px.bar(df, x='City', y='Wind Speed', title="Wind speed (km/h)",
                      labels={"City": "Cities", "Wind Speed": "Wind speed"})
    rain_fig = px.bar(df, x='City', y='Rain Probability', title="Rain Probability (%)",
                      labels={"City": "Города", 'Rain Probability':"Pain probability(%)"})

    output_text = f"Weather comparison for: {' - '.join([data['City'] for data in weather_data])}"

    forecast_data = []

    for city in all_cities:
        try:
            location_key = get_location_key_by_name(api_key, city)
            city_forecast = get_forecast(api_key, location_key, days=5)
            for day in city_forecast:
                day['city'] = city
            forecast_data.extend(city_forecast)
        except Exception as e:
            return [html.Div(f"Error for city {city}: {str(e)}")]

    df = pd.DataFrame(forecast_data)
    df = df[df["day_count"] <= int(days_c)]

    try:
        graphs = []

        graphs.append(dcc.Graph(
            figure=px.line(df, x='date', y='max_temp', color='city', title="Max temp per day (°C)",
                           labels={"date": "date", "max_temp": "maximum temperature"})
        ))
        graphs.append(dcc.Graph(
            figure=px.line(df, x='date', y='min_temp', color='city', title="Min temp per day (°C)",
                           labels={"date": "date", "min_temp": "Minimal temperature"})
        ))
        graphs.append(dcc.Graph(
            figure=px.line(df, x='date', y='precipitation_probability', color='city', title="Rain probability (%)",
                           labels={"date": "date", "precipitation_probability": "Rain probability"})
        ))
        graphs.append(dcc.Graph(
            figure=px.line(df, x='date', y='wind_speed', color='city', title="Wind speed (km/h)",
                           labels={"date": "date", "wind_speed": "Wind speed "})
        ))
    except Exception as e:
        return [html.Div(f"Error for city {city}: {str(e)}")]

    return output_text, temp_fig, humidity_fig, wind_fig, rain_fig, graphs


if __name__ == '__main__':
    app.run(debug=True)