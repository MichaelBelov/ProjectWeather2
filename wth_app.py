import requests


def concat_conditions(current_response, forecast_response):

    response = dict()
    try:
        response['text_conditions'] = current_response['WeatherText']
        response['temperature'] = current_response['Temperature']['Metric']['Value']
        response['humidity'] = current_response['RelativeHumidity']
        response['wind_speed'] = current_response['Wind']['Speed']['Metric']['Value']
        response['precipitation_probability'] = forecast_response['PrecipitationProbability']

        return response
    except TypeError:
        raise TypeError('что-то не так на стороне API AccuWeather, проверьте лимит запросов')
    except IndexError:
        raise IndexError('ошибка с API AccuWeather, проверьте лимит запросов')


def get_cur_conditions(api_key, location_key, lanquage='ru-RU'):
    url = f'http://dataservice.accuweather.com/currentconditions/v1/{location_key}'
    data = {
        'apikey': api_key,
        'lanquage': lanquage,
        'details': 'true'
    }
    try:
        current_response = requests.get(url, params=data)
        cur_data = current_response.json()[0]

        url = f'http://dataservice.accuweather.com/forecasts/v1/hourly/1hour/{location_key}'
        data = {
            'apikey': api_key,
            'lanquage': lanquage,
            'details': 'true',
            'metric': 'true'
        }

        forecast_response = requests.get(url, params=data)
        forc_data = forecast_response.json()[0]

        return concat_conditions(cur_data, forc_data)

    except TypeError:
        raise TypeError('Скорее всего произошла ошибка на стороне API AccuWeather, проверьте лимит запросов')
    except IndexError:
        raise IndexError('Скорее всего произошла ошибка на стороне API AccuWeather, проверьте лимит запросов')


def get_forecast(api_key, location_key, days=5, language='ru-RU'):
    forecast_list = []
    url = f'http://dataservice.accuweather.com/forecasts/v1/daily/{days}day/{location_key}'
    params = {
        'apikey': api_key,
        'language': language,
        'metric': 'true',
        'details': 'true'
    }
    try:
        response = requests.get(url, params=params)
        forecast_data = response.json()['DailyForecasts']

        forecast_data = response.json()['DailyForecasts']
        for i in range(len(forecast_data)):
            forecast = {
                'day_count': i+1,
                'date': forecast_data[i]['Date'],
                'min_temp': forecast_data[i]['Temperature']['Minimum']['Value'],
                'max_temp': forecast_data[i]['Temperature']['Maximum']['Value'],
                'humidity': forecast_data[i]['Day']['RelativeHumidity'],
                'wind_speed': forecast_data[i]['Day']['Wind']['Speed']['Value'],
                'precipitation_probability': forecast_data[i]['Day']['PrecipitationProbability']
                }
            forecast_list.append(forecast)
        return forecast_list

    except TypeError:
        raise TypeError('Скорее всего произошла ошибка на стороне API AccuWeather, проверьте лимит запросов')
    except IndexError:
        raise IndexError('Скорее всего произошла ошибка на стороне API AccuWeather, проверьте лимит запросов')


def get_location_key_by_name(api_key, name, lanquage='ru-RU'):

    url = 'http://dataservice.accuweather.com/locations/v1/cities/search'
    data = {
        'apikey': api_key,
        'q': name,
        'lanquage': lanquage,
        'alias': 'Always'
    }

    try:
        response = requests.get(url, params=data)
        data = response.json()

        return data[0]['Key']
    except KeyError:
        raise KeyError('Такого города нет или произошла ошибка на стороне API AccuWeather, проверьте лимит запросов')
    except TypeError:
        raise TypeError('Скорее всего произошла ошибка на стороне API AccuWeather, проверьте лимит запросов')
    except IndexError:
        raise IndexError('Скорее всего произошла ошибка на стороне API AccuWeather, проверьте лимит запросов')


def get_location_key_by_coors(coordinates, apikey, language="ru-RU"):

    url = 'http://dataservice.accuweather.com/locations/v1/cities/geoposition/search'
    data = {
        'apikey': apikey,
        'q': ','.join(list(map(str, list(coordinates)))),
        'lanquage': language
    }

    try:
        response = requests.get(url, params=data)
        data = response.json()
        return data["Key"]
    except KeyError:
        raise KeyError('Возможно, допущена ошибка при введении координат или произошла'
                       ' ошибка на стороне API AccuWeather, проверьте лимит запросов')
    except TypeError:
        raise TypeError('Скорее всего произошла ошибка на стороне API AccuWeather, проверьте лимит запросов')
    except IndexError:
        raise IndexError('Скорее всего произошла ошибка на стороне API AccuWeather, проверьте лимит запросов')