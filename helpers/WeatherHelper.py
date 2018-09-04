import urllib.parse
import urllib.request
import json


def getYahooWeather(latitude, longitude):
    woeid_base_url = 'https://query.yahooapis.com/v1/public/yql?'
    woeid_yql_query = "select woeid from geo.places where text='(" + str(latitude) + "," + str(longitude) + ")' limit 1"
    woeid_yql_url = woeid_base_url + urllib.parse.urlencode({'q': woeid_yql_query}) + '&diagnostics=false&format=json'
    woeid_result = urllib.request.urlopen(woeid_yql_url).read().decode('utf-8')
    woeid_data = json.loads(woeid_result)
    woeid = woeid_data['query']['results']['place']['woeid']

    weather_baseurl = "https://query.yahooapis.com/v1/public/yql?"
    weather_yql_query = "select * from weather.forecast where woeid=" + str(woeid) + " and u='c'"
    weather_yql_url = weather_baseurl + urllib.parse.urlencode({'q': weather_yql_query}) + "&format=json"
    weather_result = urllib.request.urlopen(weather_yql_url).read().decode('utf-8')
    weather_data = json.loads(weather_result)
    # print(weather_data)
    return weather_data


def getOpenWeather(latitude, longitude):
    forecast_url = 'https://api.openweathermap.org/data/2.5/forecast?lat=' + str(latitude) + '&lon=' + str(
        longitude) + '&units=metric&APPID=069ee95b3efe4f4992032da6fe9ac371'
    forecast_result = urllib.request.urlopen(forecast_url).read().decode('utf-8')
    forecast_data = json.loads(forecast_result)
    currentWeather_url = 'https://api.openweathermap.org/data/2.5/weather?lat=' + str(latitude) + '&lon=' + str(
        longitude) + '&units=metric&APPID=069ee95b3efe4f4992032da6fe9ac371'
    currentWeather_result = urllib.request.urlopen(currentWeather_url).read().decode('utf-8')
    currentWeather_data = json.loads(currentWeather_result)

    time = []
    windSpeed = []
    windDirection = []
    cloudCover = []
    time.append(int(currentWeather_data["dt"]))
    windSpeed.append(float(currentWeather_data["wind"]["speed"]))
    windDirection.append(float(currentWeather_data["wind"]["deg"]))
    cloudCover.append(int(currentWeather_data["clouds"]["all"]))

    for i in range(1, len(forecast_data["list"]) + 1):
        time.append(int(forecast_data["list"][i - 1]["dt"]))
        windSpeed.append(float(forecast_data["list"][i - 1]["wind"]["speed"]))
        windDirection.append(float(forecast_data["list"][i - 1]["wind"]["deg"]))
        cloudCover.append(int(forecast_data["list"][i - 1]["clouds"]["all"]))

    weatherDict = {"time": time, "windSpeed": windSpeed, "windDirection": windDirection, "cloudCover": cloudCover}
    # print("Weather data recovered")
    return weatherDict
