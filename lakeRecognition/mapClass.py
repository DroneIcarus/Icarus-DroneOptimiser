import cv2
from math import radians, cos, sin, asin, sqrt
from lakeRecognition import waterImage
from lakeRecognition.lakeClass import Lakes
from helpers.GMapsHelper import GMAPS_IMAGE_SIZE_REFERENCE, tile_to_latlon, xypixel_to_mapcoordinate, pixelcoord_to_latlon, get_google_maps_image, Coordinate, latlon_to_tile


class Map:
    def __init__(self, start_coord, end_coord):
        self.orig_im_tile, self.lakeList, self.stacked_im, self.processed_im = self.find_water_contour(start_coord,
                                                                                                       end_coord)

    def find_water_contour(self, start_coord, end_coord):
        # Fetch images between start and end coordinates
        map_tile, stacked_im = waterImage.get_waterbodies_by_startend(start_coord, end_coord)
        processed_im = self.process_map_images(stacked_im)
        resolution = self.map_meters_per_pixel(map_tile)

        # Let opencv find contours and identifies all different water bodies
        lakeList = []
        useless_im, contour, hierarchy = cv2.findContours(processed_im, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        i = 0
        j = []

        for c in contour:
            if (hierarchy[0][i][3] == 0) and (cv2.contourArea(c) > 200):
                j.append(i)
            i += 1

        # Creating a lake list with map resolution
        [lakeList.append(Lakes(contour[i], cv2.contourArea(contour[i]), resolution)) for i in j]

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

    # Find the (lat, lon) from the given stacked images point
    # TODO: Change tile  for  actual (lat,lon)
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


if __name__ == "__main__":
    coord = tile_to_latlon(latlon_to_tile(Coordinate(47.748424, -72.902954)))
    print("Initial coord: {}".format(coord))
    map1 = Map(coord, coord)
    xylatlon = map1.xy2LatLon([0,0])
    print("Final coord: {}".format(xylatlon))
    print("map_pixel: {}".format(map1.orig_im_tile))
