import configparser
import pymongo
from bson.binary import Binary
import pickle
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
__db_waterbodies = __db["waterbodies_landingpoints"]


def get_waterbody(xtile, ytile, zoom=GMAPS_ZOOM):
    tilecoord = maphelper.xytile_to_tilecoordinate(xtile, ytile)
    item = __search_waterbody_db(tilecoord)
    if item is not None:
        # The item is already in the DB
        print("In the DB")
        return pickle.loads(item['image'])
    else:
        # The item needs to be inserted in the DB
        coordtile = maphelper.tile_to_latlon(tilecoord, zoom)
        image = maphelper.get_google_maps_image(coordtile)

        # Make the transformation from image to landing points

        item = image
        if __insert_waterbody_db(tilecoord, item) is False:
            print("There was an error while inserting tile to DB. EXITING")
            exit(-1)
        else:
            print("Inserted in the DB")
            return item


# Fetch (lat,lon) corresponding tile
def get_waterbody_by_coordinate(lat, lon, zoom=GMAPS_ZOOM):
    tilecoord = maphelper.latlon_to_tile(maphelper.latlon_to_coordinate(float(lat), float(lon)), zoom)
    return get_waterbody(tilecoord.xtile, tilecoord.ytile, zoom)


def get_waterbodies_by_startend(start_coord, end_coord, zoom=GMAPS_ZOOM):
    import numpy as np
    # Convert (lat,lon) to (x,y) tiles in order to construct easily a picture of all required tiles
    start_tile_coord = maphelper.latlon_to_tile(maphelper.latlon_to_coordinate(float(start_coord.lat),
                                                                               float(start_coord.lon)), zoom)
    end_tile_coord = maphelper.latlon_to_tile(maphelper.latlon_to_coordinate(float(end_coord.lat),
                                                                               float(end_coord.lon)), zoom)
    # Sorting so it is the smallest number to the biggest
    x = sorted([start_tile_coord.xtile, end_tile_coord.xtile])
    y = sorted([start_tile_coord.ytile, end_tile_coord.ytile])

    # Inclusive loop creating tiles array and rows pictures
    xy_tiles = []
    rows = []
    j_it = 0
    for j in range(y[0], y[1] + 1):
        xy_tiles.append([])
        for i in range(x[0], x[1] + 1):
            print("X,Y = {},{}".format(i, j))
            xy_tiles[j_it].append(get_waterbody(i, j))
        rows.append(np.hstack(xy_tiles[j_it][:]))
        j_it += 1

    # Creating a picture with rows pictures
    return maphelper.TileCoordinate(x[0], y[0]), np.vstack(rows[:])


# Look if the tile (x,y) is in its database. Return the tile or None
def __search_waterbody_db(tile_coord):
    tile_no = maphelper.tile_no_by_tile_coord(tile_coord)
    return __db_waterbodies.find_one({"tile_no": tile_no})


# Insert the tile in its database
def __insert_waterbody_db(tile_coord, image):
    tile_no = maphelper.tile_no_by_tile_coord(tile_coord)
    item = __db_waterbodies.insert_one({"tile_no": tile_no,
                                        "image": Binary(pickle.dumps(image, protocol=pickle.HIGHEST_PROTOCOL))})
    if item is not None:
        return True
    else:
        return False


# The total number of tiles is calculated by:  2 ** (zoom*2)
# Eg.: For a zoom of 14; 16384 * 16384 = 268435456 tiles
if __name__ == "__main__":
    import cv2
    import numpy as np
    print("Main of waterImage.py")
    a = maphelper.Coordinate(43.156199, -82.235377)
    b = maphelper.Coordinate(43.563453, -81.750665)
    im = get_waterbodies_by_startend(b, a)
    cv2.imwrite('lakeRecognition/WaterBodiesImages/stacked_im.jpg', im)
