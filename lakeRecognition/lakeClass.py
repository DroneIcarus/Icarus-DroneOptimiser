import cv2
import sys, os.path
import numpy as np
from math import radians, degrees, cos, sin, sqrt
from helpers.GPSHelper import bearingQuadrantAngle, calcBearing, calcGPSDestination, distBetweenCoord
from operator import itemgetter

debugMode = False


def debug(str):
    if debugMode:
        print(str)


class Lakes:

    def __init__(self, lakeContour, lakeArea, resolution):
        self.lakeContour = lakeContour
        self.lakeArea = lakeArea
        self.resolution = resolution
        self.landingPoint = []
        self.gpsLandingPoint = []
        self.width, self.height = self.__getWidthHeight()

    def __getWidthHeight(self):
        x1, y1 = self.lakeContour.min(axis=0)[0]
        x2, y2 = self.lakeContour.max(axis=0)[0]
        width = y2 - y1
        height = x2 - x1
        return width, height

    def __addSortLandingPoint(self, gpsListPoint, distanceOffset):
        points = []
        sortList = []
        maxLat = None
        minLat = None
        maxLong = None
        minLong = None
        addMorePoint = False

        if len(gpsListPoint) > 0 :
            maxLat = max(gpsListPoint,key=itemgetter(0))
            minLat = min(gpsListPoint,key=itemgetter(0))
            maxLong = max(gpsListPoint,key=itemgetter(1))
            minLong = min(gpsListPoint,key=itemgetter(1))

            points.append(maxLat)
            points.append(minLat)
            points.append(maxLong)
            points.append(minLong)

            #Remove the points near the maximal and minimal points
            for point in gpsListPoint:
                if (
                distBetweenCoord(maxLong[0],maxLong[1], point[0], point[1]) > distanceOffset and
                distBetweenCoord(minLong[0],minLong[1], point[0], point[1]) > distanceOffset and
                distBetweenCoord(maxLat[0],maxLat[1], point[0], point[1]) > distanceOffset and
                distBetweenCoord(minLat[0],minLat[1], point[0], point[1]) > distanceOffset
                ):
                    sortList.append(point)

            addMorePoint = distBetweenCoord(maxLong[0],maxLong[1], minLong[0], minLong[1]) > distanceOffset or distBetweenCoord(maxLat[0],maxLat[1], minLat[0], minLat[1]) > distanceOffset

        #Delete the duplicate points
        points = list(set(points))

        return points, sortList, addMorePoint

    def getSortLandingPoint(self, maxDistance):
        points = []
        distanceOffset = maxDistance/2
        tmpPoints, newSortList, addMorePoint = self.__addSortLandingPoint(self.gpsLandingPoint, distanceOffset)
        points = points + tmpPoints

        while addMorePoint:
            tmpPoints, newSortList, addMorePoint = self.__addSortLandingPoint(newSortList, distanceOffset)
            points = points + tmpPoints

        #Delete the duplicate points
        points = list(set(points))
        return points

    def getContourPoint(self):
        points = []
        right = self.xCenter + (self.height/2)
        bottom = self.yCenter + (self.width/2)
        left = self.xCenter - (self.height/2)
        top = self.yCenter - (self.width/2)

        bottomRight = self.mapObject.xy2LatLon([right, bottom])
        bottomLeft = self.mapObject.xy2LatLon([left, bottom])
        topRight = self.mapObject.xy2LatLon([right, top])
        topLeft = self.mapObject.xy2LatLon([left, top])
        centerLeft = self.mapObject.xy2LatLon([left, self.yCenter])
        centerRight = self.mapObject.xy2LatLon([right, self.yCenter])
        centerTop = self.mapObject.xy2LatLon([self.xCenter, top])
        center = self.mapObject.xy2LatLon([self.xCenter, self.yCenter])
        points.append(center)
        points.append(bottomRight)
        points.append(bottomLeft)
        points.append(topRight)
        points.append(topLeft)

        return points
        # print("centerPoint: ", self.centerPoint)
        # print("bottomRight", bottomRight)
        # print("bottomLeft", bottomLeft)
        # print("topRight", topRight)
        # print("topLeft", topLeft)
        # print("centerRight", centerRight)
        # print("centerLeft", centerLeft)
        # print("centerTop", centerTop)

    def cropContour(self, imProcessed, mapObject):
        self.mapObject = mapObject
        x1, y1 = self.lakeContour.min(axis=0)[0]
        x2, y2 = self.lakeContour.max(axis=0)[0]
        self.xCenter = (x2 + x1) // 2
        self.yCenter = (y2 + y1) // 2
        self.centerPoint = mapObject.xy2LatLon([self.xCenter, self.yCenter])
        self.contourImage = imProcessed[y1:y2, x1:x2]
        self.lakeContour = self.lakeContour - [x1, y1]

    def xy2LatLon(self, point):
        # xc and yc are the center of the image of the lake in pixel
        # shape[0] is y and shape[1] is x at this moment... should be changed
        yc = self.contourImage.shape[0] // 2 + 1
        xc = self.contourImage.shape[1] // 2 + 1

        # https://www.movable-type.co.uk/scripts/latlong.html
        # Calculate the x,y in a cartesian plan
        yCart = yc - point[1]
        xCart = point[0] - xc
        debug("Cartesian: %s %s" % (xCart, yCart))

        # Calculate the bearing from the north
        bearing = calcBearing(xCart, yCart)

        # Calculate the distance between the lakeCenter and the point
        d = sqrt(yCart ** 2 + xCart ** 2) * self.resolution
        debug("d: %s" % d)

        # Calculate the gps coordinate of the point2
        lat2, long2 = calcGPSDestination(self.centerPoint, d/1000, bearing)
        debug("latlong %s %s" % (lat2, long2))
        return lat2, long2

    def findLandingPoint(self, weatherDict, expectedTime):
        self.landingPoint[:] = []
        self.gpsLandingPoint[:] = []
        timeIndex = weatherDict["time"].index(min(weatherDict["time"], key=lambda x: abs(x - expectedTime)))
        # print(weatherDict["windDirection"][timeIndex])
        if (weatherDict["windDirection"][timeIndex] <= 90):
            windDir = -weatherDict["windDirection"][timeIndex] + 90
        else:
            windDir = -weatherDict["windDirection"][timeIndex] + 450
        # print(windDir)
        windDir = 30
        deriveSpeed = weatherDict["windSpeed"][timeIndex] * 0.02
        # Need to add sun force depending on the time of the year/day, variation of the charging time with cloud cover changing over time
        # chargingTime = 3600/(1-weatherDict["cloudCover"][timeIndex]*0.01+0.1)
        chargingTime = 2000
        derive = deriveSpeed * chargingTime // self.resolution

        point2 = [int(-derive * 1.0 * sin(radians(windDir - 10))), int(derive * 1.0 * cos(radians(windDir - 10)))]
        point3 = [int(-derive * 1.0 * sin(radians(windDir + 10))), int(derive * 1.0 * cos(radians(windDir + 10)))]
        imax = self.contourImage.shape[0]
        jmax = self.contourImage.shape[1]

        lastJ = 0
        lastI = 0
        idetected = False

        for i in range(0, imax, 5):
            jdetected = False

            if not idetected or (idetected and i >= lastI+25):
                for j in range(0, jmax, 5):
                    if not jdetected or (jdetected and j >= lastJ+25):
                        if (i + point2[0] >= 0 and j + point2[1] >= 0 and i + point3[0] >= 0 and j + point3[1] >= 0):
                            if i + point2[0] < imax and j + point2[1] < jmax and i + point3[0] < imax and j + point3[1] < jmax:
                                pointsAreInside = True
                            else:
                                pointsAreInside = False
                        else:
                            pointsAreInside = False
                        if (cv2.pointPolygonTest(self.lakeContour, (j, i), False) >= 0 and pointsAreInside):
                            point = np.array([[j, i], [j + point2[1], i + point2[0]], [j + point3[1], i + point3[0]]])
                            tempImage = np.copy(self.contourImage)
                            cv2.fillConvexPoly(tempImage, point, 0)

                            #Add a circle to assure that there are no land near the landing point
                            tempImage2 = np.copy(self.contourImage)
                            cv2.circle(tempImage2,(j, i), 10, 0, -1)

                            if (np.array_equal(tempImage, self.contourImage)) and (np.array_equal(tempImage2, self.contourImage)):
                                self.landingPoint.append([i, j])
                                self.gpsLandingPoint.append(self.xy2LatLon([j, i]))
                                cv2.circle(tempImage2,(i, j), 10, 0, -1)
                                jdetected = True
                                idetected = True
                                lastJ = j
                                lastI = i


        for lp in self.landingPoint:
            self.contourImage[lp[0], lp[1]] = 255

        cv2.imwrite("satelliteImages/" + str(self.centerPoint) + ".jpg", self.contourImage)
        # print(len(self.landingPoint))
        # print("There is %d landing point" % (len(self.gpsLandingPoint)))
        return self.gpsLandingPoint


    def getLandingPoint(self):
        # temp= []
        # temp.append([self.centerPoint])
        # return temp

        return self.gpsLandingPoint

        # return self.getContourPoint()

    def getLakeCenter(self):
        return self.centerPoint
