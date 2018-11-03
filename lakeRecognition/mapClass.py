import sys
import cv2
import numpy as np
import os
from math import radians, cos, sin, asin, sqrt
from lakeRecognition import waterImage
from lakeRecognition.lakeClass import Lakes


class Map:
    def __init__(self, startLatitude, startLongitude, endLatitude, endLongitude):
        self.lakeContour = []
        self.contour = []
        self.lakeArea = []

        self.longNext = 0.05155
        self.latNext = -0.00000636 * float(startLatitude) ** 2 - 0.00005506 * float(startLatitude) + 0.05190551

        self.latitudeDir = 'up' if float(startLatitude) < float(endLatitude) else 'down'
        self.latitudeIt = np.ceil(np.absolute(float(startLatitude) - float(endLatitude)) / self.latNext) // 2 * 2 + 1

        if (self.latitudeDir == 'down'):
            self.latitude = [float(startLatitude) - i * self.latNext for i in range(0, self.latitudeIt.astype(int))]
        elif (self.latitudeDir == 'up'):
            self.latitude = [float(endLatitude) - i * self.latNext for i in range(0, self.latitudeIt.astype(int))]

        self.longitudeDir = 'left' if float(startLongitude) < float(endLongitude) else 'right'
        self.longitudeIt = np.ceil(
            np.absolute(float(startLongitude) - float(endLongitude)) / self.longNext) // 2 * 2 + 1
        if (self.longitudeDir == 'left'):
            self.longitude = [float(startLongitude) + i * self.longNext for i in range(0, self.longitudeIt.astype(int))]
        elif (self.longitudeDir == 'right'):
            self.longitude = [float(endLongitude) + i * self.longNext for i in range(0, self.longitudeIt.astype(int))]

        self.horizontalCenter = self.longitude[(self.longitudeIt // 2 + 1).astype(int) - 1]
        self.verticalCenter = self.latitude[(self.latitudeIt // 2 + 1).astype(int) - 1]

        croppedImage = [[None for _ in range(self.longitudeIt.astype(int))] for _ in range(self.latitudeIt.astype(int))]
        for i in range(0, self.latitudeIt.astype(int)):
            for j in range(0, self.longitudeIt.astype(int)):
                croppedImage[i][j] = self.getSatelliteImage(str("{0:.6f}".format(self.latitude[i])),
                                                            str("{0:.6f}".format(self.longitude[j])))
        self.imageAdded = self.addImages(croppedImage)
        self.resolution = self.distanceXY([0, 0], [0, 1])

    # Used only in here
    def getSatelliteImage(self, lat, lon):
        image = waterImage.get_waterbody(lat, lon)
        if image is not None:
            imCropped = self.cropImage(image)
            return imCropped
        else:
            sys.exit("Error: Fetching water image was unsuccessful. EXITING.")

    # Used in MissionPanner.py
    def satImageProcess(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
        thresh = cv2.threshold(blurred, 60, 255, cv2.THRESH_BINARY)[1]
        cv2.rectangle(thresh, (0, 0), (image.shape[1], image.shape[0]), 255, 3)
        cv2.imwrite('lakeRecognition/WaterBodiesImages/thresh.jpg', thresh)
        return thresh

    # Used in MissionPanner.py
    def findLakeContour(self, imageFiltered, originalImage, lakeList):
        _, contour, hierarchy = cv2.findContours(imageFiltered, cv2.RETR_TREE,
                                                 cv2.CHAIN_APPROX_NONE)
        i = 0
        j = []

        for c in contour:
            if (hierarchy[0][i][3] == 0) and (cv2.contourArea(c) > 200):
                j.append(i)
            i += 1

        [lakeList.append(Lakes(contour[i], cv2.contourArea(contour[i]), self.resolution)) for i in j]

        cv2.drawContours(originalImage, [lake.lakeContour for lake in lakeList], -1, (0, 0, 255))
        cv2.imwrite('lakeRecognition/WaterBodiesImages/final.jpg', originalImage)
        # print("Lake contour detected")
        return originalImage

    # Used only in here
    def addImages(self, images):
        line = len(images)
        column = len(images[0])
        lineAdded = [None for _ in range(line)]
        for i in range(line):
            lineAdded[i] = np.hstack(images[i][:])
        if line > 0:
            finalImage = np.vstack(lineAdded[:])
        else:
            finalImage = lineAdded[0]
        cv2.imwrite('lakeRecognition/WaterBodiesImages/imageAdded.jpg', finalImage)
        # print("Map constructed")
        return finalImage

    # TODO: TOBE DELETED!
    # Used only in here
    def cropImage(self, image):
        image = np.asarray(bytearray(image), dtype="uint8")
        image = cv2.imdecode(image, cv2.IMREAD_COLOR)
        #return image
        image = image[0:-19, 0:-19]
        return image

    # Used only in here
    def xy2LatLon(self, point):
        xCenter = self.imageAdded.shape[1] // 2 + 1
        yCenter = self.imageAdded.shape[0] // 2 + 1
        lon = self.horizontalCenter + (point[0] - xCenter) * self.longNext / 601
        lat = self.verticalCenter + (yCenter - point[1]) * self.latNext / 601
        return lat, lon

    # Used only in here
    def distanceXY(self, point1, point2):
        lat1, lon1 = self.xy2LatLon(point1)
        lat2, lon2 = self.xy2LatLon(point2)
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * asin(sqrt(a))
        # Radius of earth in kilometers is 6371
        km = 6371 * c
        return km * 1000
