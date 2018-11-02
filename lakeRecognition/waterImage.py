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


# As of right now, it is only fetching the latlong corresponding tile
def get_waterbody(lat, lon, zoom=GMAPS_ZOOM):
    tilecoord = maphelper.latlon_to_tile(maphelper.latlon_to_coordinate(float(lat), float(lon)), zoom)
    item = search_waterbody_db(tilecoord)
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
        if insert_waterbody_db(tilecoord, item) is False:
            print("There was an error while inserting tile to DB. EXITING")
            exit(-1)
        else:
            print("Inserted in the DB")
            return item


# Look if the tile (x,y) is in its database. Return the tile or None
def search_waterbody_db(tile_coord):
    tile_no = maphelper.tile_no_by_tile_coord(tile_coord)
    return __db_waterbodies.find_one({"tile_no": tile_no})


# Insert the tile in its database
def insert_waterbody_db(tile_coord, image):
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
    print("Main of waterImage.py")

    im = get_waterbody(44.166444664458595, -74.3994140625)
    im1 = get_waterbody(44.166444664458595, -74.37744140625)
    im2 = get_waterbody(44.166444664458595, -74.35546875)

    cv2.imwrite('/tmp/im.jpg', im)
    cv2.imwrite('/tmp/im1.jpg', im1)
    cv2.imwrite('/tmp/im2.jpg', im2)
