import sys
import logging
from MissionPlanner.Weather import Weather
from helpers.WeatherHelper import getOpenWeather

class LongWeather:
    def __init__(self, latitude, longitude):
        self.__latitude = latitude
        self.__longitude = longitude
        self.__checkLatitudeLongitude()
        self.__longWeather = getOpenWeather(self.__latitude, self.__longitude);

    def __checkLatitudeLongitude(self):
        if self.__latitude == None or self.__longitude == None:
            print("ERROR - Coordinates for generating the LongWeather is not valid")
            sys.exit()

    def __checkExpectedTime(self, expectedTime, timeIndex):
        #86400 is equivalent to one day
        if(abs(self.__longWeather["time"][timeIndex] - expectedTime) > 86400):
            print("No precise weather near the expected time...")
            sys.exit()

    def getLongWeather(self):
        return self.__longWeather

    def getWeather(self, expectedTime):
        timeIndex = self.__longWeather["time"].index(min(self.__longWeather["time"], key=lambda x: abs(x -expectedTime)))
        self.__checkExpectedTime(expectedTime, timeIndex)
        return Weather(self.__latitude, self.__longitude, self.__longWeather["time"][timeIndex], self.__longWeather["windDirection"][timeIndex],
                        self.__longWeather["windSpeed"][timeIndex], self.__longWeather["cloudCover"][timeIndex])

    def getWindSpeed(self, expectedTime):
        timeIndex = self.__longWeather["time"].index(min(self.__longWeather["time"], key=lambda x: abs(x -expectedTime)))
        self.__checkExpectedTime(expectedTime, timeIndex)
        return self.__longWeather["windSpeed"][timeIndex]

    def getWindDirection(self, expectedTime):
        timeIndex = self.__longWeather["time"].index(min(self.__longWeather["time"], key=lambda x: abs(x -expectedTime)))
        self.__checkExpectedTime(expectedTime, timeIndex)
        return self.__longWeather["windDirection"][timeIndex]

    def getCloudCover(self, expectedTime):
        timeIndex = self.__longWeather["time"].index(min(self.__longWeather["time"], key=lambda x: abs(x -expectedTime)))
        self.__checkExpectedTime(expectedTime, timeIndex)
        return self.__longWeather["cloudCover"][timeIndex]
