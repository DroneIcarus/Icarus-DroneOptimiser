import cv2
from math import radians, cos, sin, asin, sqrt
from lakeRecognition import waterImage
from lakeRecognition.lakeClass import Lakes
from helpers.GMapsHelper import GMAPS_IMAGE_SIZE_REFERENCE, tile_to_latlon, xypixel_to_mapcoordinate, pixelcoord_to_latlon, get_google_maps_image, Coordinate, latlon_to_tile, xytile_to_tilecoordinate, TileCoordinate


class Map:
    def __init__(self, start_coord, end_coord):
        self.orig_im_tile, self.lakeList = self.waterbody_contours(start_coord, end_coord)

    def waterbody_contours(self, start_coord, end_coord):

        # Get contours for every tile between start-end coordinates
        map_base_tile, map_contours_hierarchy = waterImage.get_waterbodies_by_startend(start_coord, end_coord)

        contours = []
        hierarchy = []
        for ch in map_contours_hierarchy:
            contours.append(ch[0])
            hierarchy.append(ch[1])

        # Find resolution using the base tile
        #resolution = self.map_meters_per_pixel(map_base_tile)
        resolution = 6.415610451894849
        lakeList = []
        i = 0
        j = []

        for c in map_contours:
            if (hierarchy[0][i][3] == 0) and (cv2.contourArea(c) > 200):
                j.append(i)
            i += 1

        # Creating a lake list with map resolution
        [lakeList.append(Lakes(map_contours[i], cv2.contourArea(contour[i]), resolution)) for i in j]

        #cv2.drawContours(stacked_im, [lake.lakeContour for lake in lakeList], -1, (0, 0, 255))
        #cv2.imwrite('lakeRecognition/WaterBodiesImages/final.jpg', stacked_im)

        return map_base_tile, lakeList

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


def process_map_images(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)
    thresh = cv2.threshold(blurred, 60, 255, cv2.THRESH_BINARY)[1]
    cv2.rectangle(thresh, (0, 0), (image.shape[1], image.shape[0]), 255, 3)
    cv2.imwrite('lakeRecognition/WaterBodiesImages/thresh.jpg', thresh)
    return thresh


if __name__ == "__main__":
    a = tile_to_latlon(TileCoordinate(4874, 5711))
    b = tile_to_latlon(TileCoordinate(4875, 5711))

    Map(a, b)


    print("PART 2")
    import numpy as np
    start_coord = Coordinate(47.70407055468608, -72.88831261)
    end_coord = Coordinate(47.76779345, -72.80118764275467)
    resolution = 6.415610451894849

    im1 = waterImage.get_waterbody(4874, 5711)
    processed_im1 = process_map_images(im1)
    useless_im1, contour1, hierarchy1 = cv2.findContours(processed_im1, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    #print(contour1)

    im2 = waterImage.get_waterbody(4875, 5711)
    processed_im2 = process_map_images(im2)
    useless_im2, contour2, hierarchy2 = cv2.findContours(processed_im2, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE, offset=(256,0))
    #print(hierarchy2)

    stacked_im = np.hstack([im1, im2])
    contour = contour1 + contour2 #np.hstack([contour1, contour2])
    print(contour)
    hierarchy = np.hstack([hierarchy1, hierarchy2])
    #print(hierarchy)
    lakeList = []

    i = 0
    j = []

    for c in contour:
        if (hierarchy[0][i][3] == 0) and (cv2.contourArea(c) > 200):
            j.append(i)
        i += 1

    # Creating a lake list with map resolution
    [lakeList.append(Lakes(contour[x], cv2.contourArea(contour[x]), resolution)) for x in j]

    cv2.drawContours(stacked_im, [lake.lakeContour for lake in lakeList], -1, (0, 0, 255))
    cv2.imwrite('lakeRecognition/WaterBodiesImages/final.jpg', stacked_im)
