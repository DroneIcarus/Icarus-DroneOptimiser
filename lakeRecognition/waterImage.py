import configparser
import pymongo
import pickle
import cv2
import numpy as np
from bson.binary import Binary
import helpers.GMapsHelper as maphelper

################### Constants ###################
GMAPS_ZOOM = maphelper.get_zoom()
MAX_TILE_SIZE = maphelper.get_tile_size()

################### Config File ###################
config = configparser.ConfigParser()
config.read('config.ini')

################### Database ###################
__DB_path = "mongodb://" + config['database']['url'] + ":" + config['database']['port']
__dbclient = pymongo.MongoClient(__DB_path)
__db = __dbclient[config['database']['name']]
__db_waterbodies = __db["waterbodies_contour"]


###################################################################
#
# Retrieving & Manipulation functions for water body images
#
###################################################################

def get_waterbody(xtile, ytile, zoom=GMAPS_ZOOM):
    tilecoord = maphelper.xytile_to_tilecoordinate(xtile, ytile)
    item = __search_waterbody_db(tilecoord)
    if item is not None:
        # Item is already in the DB
        print("{} already in the DB".format(tilecoord))
        return pickle.loads(item['contour']), pickle.loads(item['hierarchy'])
    else:
        # The item needs to be inserted in the DB
        coordtile = maphelper.tile_to_latlon(tilecoord, zoom)
        image = maphelper.get_google_maps_image(coordtile)

        # Make the transformation from image to landing points
        contour, hierarchy = __find_waterbody_contour(image)

        if __insert_waterbody_db(tilecoord, contour, hierarchy) is False:
            print("There was an error while inserting tile data to DB. EXITING")
            exit(-1)
        else:
            print("{} has been inserted in the DB".format(tilecoord))
            return contour, hierarchy


# Fetch (lat,lon) corresponding tile
def get_waterbody_by_coordinate(coord, zoom=GMAPS_ZOOM):
    tilecoord = maphelper.latlon_to_tile(coord, zoom)
    return get_waterbody(tilecoord.xtile, tilecoord.ytile, zoom)


def get_waterbodies_by_startend(start_coord, end_coord, zoom=GMAPS_ZOOM):
    # Convert (lat,lon) to (x,y) tiles in order to construct easily a picture of all required tiles
    start_tile_coord = maphelper.latlon_to_tile(maphelper.latlon_to_coordinate(float(start_coord.lat),
                                                                               float(start_coord.lon)), zoom)
    end_tile_coord = maphelper.latlon_to_tile(maphelper.latlon_to_coordinate(float(end_coord.lat),
                                                                               float(end_coord.lon)), zoom)
    # Sorting so it is the smallest number to the biggest
    x = sorted([start_tile_coord.xtile, end_tile_coord.xtile])
    y = sorted([start_tile_coord.ytile, end_tile_coord.ytile])

    # Inclusive loop creating tiles array and rows pictures
    contours = []
    hierarchies = np.array([])

    rows = []
    j_it = 0
    a = 0
    for j in range(y[0], y[1] + 1):
        for i in range(x[0], x[1] + 1):
            c, h = get_waterbody(i, j)
            if a is 0:
                contours = c
                hierarchies = h
            contours += c
            hierarchies = np.hstack([hierarchies, h])
        j_it += 1

    map_size = maphelper.MapCoordinate(y[1]-y[0], x[1]-x[0])
    # Creating a picture with rows pictures
    return maphelper.TileCoordinate(x[0], y[0]), map_size, contours, hierarchies


def __find_waterbody_contour(wb_image):
    processed_im = __process_map_images(wb_image)

    # Let opencv finds all contour of different water bodies
    useless_im, contour, hierarchy = cv2.findContours(processed_im, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    return contour, hierarchy


def __process_map_images(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)
    thresh = cv2.threshold(blurred, 60, 255, cv2.THRESH_BINARY)[1]
    cv2.rectangle(thresh, (0, 0), (image.shape[1], image.shape[0]), 255, 3)
    cv2.imwrite('lakeRecognition/WaterBodiesImages/thresh.jpg', thresh)
    return thresh

###################################################################
#
# Database communication functions
#
###################################################################


# Look if the tile (x,y) is in its database. Return the tile or None
def __search_waterbody_db(tile_coord):
    tile_no = maphelper.tile_no_by_tile_coord(tile_coord)
    return __db_waterbodies.find_one({"tile_no": tile_no})


# Insert the tile in its database
def __insert_waterbody_db(tile_coord, contour, hierarchy):
    tile_no = maphelper.tile_no_by_tile_coord(tile_coord)
    item = __db_waterbodies.insert_one({"tile_no": tile_no,
                                        "contour": Binary(pickle.dumps(contour, protocol=pickle.HIGHEST_PROTOCOL)),
                                        "hierarchy": Binary(pickle.dumps(hierarchy, protocol=pickle.HIGHEST_PROTOCOL))})
    if item is not None:
        return True
    else:
        return False


# The total number of tiles is calculated by:  2 ** (zoom*2)
# Eg.: For a zoom of 14; 16384 * 16384 = 268435456 tiles
if __name__ == "__main__":
    import cv2
    print("Main of waterImage.py")
    a = maphelper.Coordinate(43.156199, -82.235377)
    b = maphelper.Coordinate(43.563453, -81.750665)
    im = get_waterbodies_by_startend(b, a)
    cv2.imwrite('lakeRecognition/WaterBodiesImages/stacked_im.jpg', im)
