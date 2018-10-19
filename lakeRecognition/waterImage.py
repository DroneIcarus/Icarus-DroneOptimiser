import configparser
import pymongo
from helpers.GMapsHelper import get_google_maps_image

config = configparser.ConfigParser()
config.read('config.ini')

__DB_path = "mongodb://" + config['database']['url'] + ":" + config['database']['port']
__dbclient = pymongo.MongoClient(__DB_path)
__db = __dbclient[config['database']['name']]
__db_waterbodies = __db["waterbodies"]


def get_waterbody_image(lat, lon):
    image_db = search_waterbody_db(lat, lon)
    if image_db is not None:
        return image_db
    else:
        image = get_google_maps_image(lat, lon)
        insert_waterbody_db(lat, lon, image)
        return image


def search_waterbody_db(lat, lon):
    return __db_waterbodies.find_one({"lat": lat, "lon": lon})


def insert_waterbody_db(lat, lon, image):
    item = __db_waterbodies.insert_one({"lat": lat, "lon": lon, "image": image})
    if item is not None:
        return True
    else:
        return False

# The total number of tiles is calculated by:  2 ** (zoom*2)
# Eg.: For a zoom of 14; 16384 * 16384 = 268435456 tiles
if __name__ == "__main__":
    lat = 44.1644712
    lon = -74.3818805
    get_waterbody_image(lat, lon)
    #mydict = {"lat": 44.1644712, "lon": -74.3818805, "image": get_waterbody_image(44.1644712, -74.3818805)}

    #x = __db_waterbodies.insert_one(mydict)

    #print(x.inserted_id)

    #print(__dbclient.list_database_names())

    #print( __db_waterbodies.find_one({"lat": 44.1644712, "lon": -74.3818805}) )
    #get_waterbody_image(44.1644712, -74.3818805)
