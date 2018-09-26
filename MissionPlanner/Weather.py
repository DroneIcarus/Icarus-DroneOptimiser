import sys

class Weather:
    def __init__(self, latitude, longitude, time, windDirection, windSpeed, cloudCover):
        self.__latitude = latitude
        self.__longitude = longitude
        self.__checkLatitudeLongitude()
        self.time = time
        self.windDirection = windDirection
        self.windSpeed = windSpeed
        self.cloudCover = cloudCover

    def __checkLatitudeLongitude(self):
        if self.__latitude == None or self.__longitude == None:
            print("ERROR - Coordinates for generating the weather point is not valid")
            sys.exit()
