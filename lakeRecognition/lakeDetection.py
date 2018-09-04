import time
from lakeRecognition.mapClass import Map
from helpers.WeatherHelper import getYahooWeather
from helpers.WeatherHelper import getOpenWeather



map1 = Map(45.384466,-72.236481,45.449293,-72.100868)

imageProcessed = map1.satImageProcess(map1.imageAdded)

lakeList = []
imageWithContour = map1.findLakeContour(imageProcessed,map1.imageAdded,lakeList)
[lake.cropContour(imageProcessed,map1) for lake in lakeList]
# print("Lake contour has been detected")

weather = getOpenWeather(map1.verticalCenter,map1.horizontalCenter)

lakeList[6].findLandingPoint(weather,int(time.time()))
#[lake.findLandingPoint(weather,int(time.time())) for lake in lakeList]
