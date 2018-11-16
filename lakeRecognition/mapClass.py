import sys
import cv2
import numpy as np
import os
from math import radians, cos, sin, asin, sqrt
from lakeRecognition import waterImage
from lakeRecognition.lakeClass import Lakes
from helpers.GMapsHelper import Coordinate, TileCoordinate, GMAPS_IMAGE_SIZE_REFERENCE, tile_to_latlon


class Map:
    def __init__(self, start_coord, end_coord):
        self.resolution = 0 # Going to be updated in map_meters_per_pixel()
        self.orig_im_tile, self.lakeList, self.stacked_im, self.processed_im = self.find_water_contour(start_coord,
                                                                                                       end_coord)

    def find_water_contour(self, start_coord, end_coord):
        # Fetch images between start and end coordinates
        map_tile, stacked_im = waterImage.get_waterbodies_by_startend(start_coord, end_coord)
        processed_im = self.process_map_images(stacked_im)
        map_resolution = self.map_meters_per_pixel(map_tile)

        # Let opencv find contours and identifies all different water bodies
        lakeList = []
        useless_im, contour, hierarchy = cv2.findContours(processed_im, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        i = 0
        j = []

        for c in contour:
            if (hierarchy[0][i][3] == 0) and (cv2.contourArea(c) > 200):
                j.append(i)
            i += 1

        # TODO: change hardcoded resolution value for the good one
        # Creating a lake list with map resolution (hard-coded)
        [lakeList.append(Lakes(contour[i], cv2.contourArea(contour[i]), self.resolution)) for i in j]

        cv2.drawContours(stacked_im, [lake.lakeContour for lake in lakeList], -1, (0, 0, 255))
        cv2.imwrite('lakeRecognition/WaterBodiesImages/final.jpg', stacked_im)

        return map_tile, lakeList, stacked_im, processed_im

    def process_map_images(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
        thresh = cv2.threshold(blurred, 60, 255, cv2.THRESH_BINARY)[1]
        cv2.rectangle(thresh, (0, 0), (image.shape[1], image.shape[0]), 255, 3)
        cv2.imwrite('lakeRecognition/WaterBodiesImages/thresh.jpg', thresh)
        return thresh

    def xy2LatLon(self, point):
        xpoint_tile_im = self.orig_im_tile.xtile + point[0] // GMAPS_IMAGE_SIZE_REFERENCE.x
        ypoint_tile_im = self.orig_im_tile.ytile + point[1] // GMAPS_IMAGE_SIZE_REFERENCE.y
        return tile_to_latlon(TileCoordinate(xpoint_tile_im, ypoint_tile_im))

    def distance(self, p1, p2):
        lat1, lon1, lat2, lon2 = map(radians, [p1.lat, p1.lon, p2.lat, p2.lon])
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * asin(sqrt(a))
        # Radius of earth in kilometers is 6371
        distance_meters = 6371000 * c
        return distance_meters

    def map_meters_per_pixel(self, base_tile):
        t1coord = tile_to_latlon(base_tile)
        t2coord = tile_to_latlon(base_tile._replace(ytile=base_tile.ytile+1))
        distance_m = self.distance(t1coord, t2coord)
        print("Answer = {}".format(distance_m/GMAPS_IMAGE_SIZE_REFERENCE.x))
        self.resolution = distance_m/GMAPS_IMAGE_SIZE_REFERENCE.x
        return distance_m/GMAPS_IMAGE_SIZE_REFERENCE.x



class Map2:
    def __init__(self, startLatitude, startLongitude, endLatitude, endLongitude):
        self.lakeContour = [] # unused
        self.contour = [] # unused
        self.lakeArea = [] # unused

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
        image = waterImage.get_waterbody_by_coordinate(lat, lon)
        if image is not None:
            return image
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
    def findLakeContour(self, imageFiltered, originalImage):
        #imageFiltered = return of satImageProcess
        #originalImage = self. imageAdded
        #lakelist... useless var arg

        lakeList = []
        useless_im, contour, hierarchy = cv2.findContours(imageFiltered, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
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
        return lakeList

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

    # Used here and in lakeClass
    def xy2LatLon(self, point):
        print(point)
        xCenter = self.imageAdded.shape[1] // 2 + 1
        yCenter = self.imageAdded.shape[0] // 2 + 1
        lon = self.horizontalCenter + (point[0] - xCenter) * self.longNext / 601
        lat = self.verticalCenter + (yCenter - point[1]) * self.latNext / 601
        print("LES LAT LON: {},{}".format(lat, lon))
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
        print("RESOLUTION: {}".format(km*1000))
        return km * 1000
