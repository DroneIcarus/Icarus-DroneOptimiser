import cv2
import numpy as np
from math import radians, cos, sin, asin, sqrt
from lakeRecognition import waterImage
from lakeRecognition.lakeClass import Lakes
from helpers.GMapsHelper import GMAPS_IMAGE_SIZE_REFERENCE, tile_to_latlon, xypixel_to_mapcoordinate, pixelcoord_to_latlon, get_google_maps_image, Coordinate, latlon_to_tile, xytile_to_tilecoordinate, TileCoordinate


class Map:
    def __init__(self, start_coord, end_coord):
        self.orig_im_tile, self.map_size, self.lakeList, self.processed_im = self.waterbody_contours(start_coord, end_coord)

    def waterbody_contours(self, start_coord, end_coord):

        # Get contours for every tile between start-end coordinates
        map_ini_tile, map_size, map_contours, map_hierarchies = waterImage.get_waterbodies_by_startend(start_coord, end_coord)

        # Find resolution using the base tile
        #resolution = self.map_meters_per_pixel(map_base_tile)
        resolution = 6.415610451894849
        lakeList = []
        i = 0
        j = []

        for c in map_contours:
            if (map_hierarchies[0][i][3] == 0) and (cv2.contourArea(c) > 200):
                j.append(i)
            i += 1

        # Creating a lake list with map resolution
        [lakeList.append(Lakes(map_contours[i], cv2.contourArea(map_contours[i]), resolution)) for i in j]

        processed_im = np.zeros((map_size.x * 256, map_size.y * 256, 3), np.uint8)
        processed_im[:] = (255, 255, 255)

        #cv2.drawContours(processed_im, [lake.lakeContour for lake in lakeList], -1, (0, 0, 255), thickness=cv2.FILLED,
        #                 offset=(-map_ini_tile.xtile * 256, -map_ini_tile.ytile * 256))
        cv2.fillPoly(processed_im, pts=[lake.lakeContour for lake in lakeList], color=(0, 0, 0),
                     offset=(-map_ini_tile.xtile * 256, -map_ini_tile.ytile * 256))
        cv2.erode(processed_im, np.ones((4, 4)), processed_im)
        cv2.imwrite('lakeRecognition/WaterBodiesImages/final.jpg', processed_im)

        return map_ini_tile, map_size, lakeList, processed_im

    # Find the (lat, lon) from the given stacked images point
    def xy2LatLon(self, point):
        map_xpixel = self.orig_im_tile.xtile * GMAPS_IMAGE_SIZE_REFERENCE.x - GMAPS_IMAGE_SIZE_REFERENCE.x/2 + point[0]
        map_ypixel = self.orig_im_tile.ytile * GMAPS_IMAGE_SIZE_REFERENCE.y - GMAPS_IMAGE_SIZE_REFERENCE.y/2 + point[1]
        return pixelcoord_to_latlon(xypixel_to_mapcoordinate(map_xpixel, map_ypixel))

    # Calculate the distance between two (lat,lon) in meters
    def distance(self, p1, p2):
        lat1, lon1, lat2, lon2 = map(radians, [p1.lat, p1.lon, p2.lat, p2.lon])
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * asin(sqrt(a))
        # Radius of earth: 6371 km
        distance_meters = 6371000 * c
        return distance_meters

    # Find actual resolution of the map. meter/px
    def map_meters_per_pixel(self, base_tile):
        t1coord = tile_to_latlon(base_tile)
        t2coord = tile_to_latlon(base_tile._replace(ytile=base_tile.ytile+1))
        distance_m = self.distance(t1coord, t2coord)
        return distance_m/GMAPS_IMAGE_SIZE_REFERENCE.x
