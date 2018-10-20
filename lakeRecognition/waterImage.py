import configparser
import pymongo
import helpers.GMapsHelper as maphelper

GMAPS_ZOOM = 14
MAX_TILE_SIZE = maphelper.get_tile_size()

config = configparser.ConfigParser()
config.read('config.ini')

__DB_path = "mongodb://" + config['database']['url'] + ":" + config['database']['port']
__dbclient = pymongo.MongoClient(__DB_path)
__db = __dbclient[config['database']['name']]
__db_waterbodies = __db["waterbodies_landingpoints"]


# As of right, it is only fetching the latlong corresponding tile
def get_waterbody(lat, lon, zoom=GMAPS_ZOOM):
    tilecoord = maphelper.latlon_to_tile(maphelper.latlon_to_coordinate(float(lat), float(lon)), zoom)
    item = search_waterbody_db(tilecoord)
    if item is not None:
        print("oui")
        return item['image']
    else:
        coordtile = maphelper.tile_to_latlon(tilecoord, zoom)
        image = maphelper.get_google_maps_image(coordtile.lat, coordtile.lon)

        # Make the transformation from image to landing points

        item = image
        if insert_waterbody_db(tilecoord, item) is False:
            print("There was an error while inserting tile to DB. EXITING")
            exit(-1)
        else:
            print("Ouioui")
            return item


def tile_no_by_tile_coord(tile_coord, max_tile_size=MAX_TILE_SIZE):
    return tile_coord.xtile + tile_coord.ytile * max_tile_size.xtile


def tile_coord_by_tile_no(tile_no, max_tile_size=MAX_TILE_SIZE):
    ytile, xtile = divmod(tile_no, max_tile_size.xtile)
    return maphelper.xytile_to_tilecoordinate(xtile, ytile)


def search_waterbody_db(tile_coord):
    tile_no = tile_no_by_tile_coord(tile_coord)
    return __db_waterbodies.find_one({"tile_no": tile_no})


def insert_waterbody_db(tile_coord, image):
    tile_no = tile_no_by_tile_coord(tile_coord)
    item = __db_waterbodies.insert_one({"tile_no": tile_no, "image": image})
    if item is not None:
        return True
    else:
        return False

# The total number of tiles is calculated by:  2 ** (zoom*2)
# Eg.: For a zoom of 14; 16384 * 16384 = 268435456 tiles
if __name__ == "__main__":
    print("Main of waterImage.py")
    #coord = maphelper.latlon_to_coordinate(44.1644712, -74.3818805)

    #print(get_waterbody(coord, 14))

    #mydict = {"lat": 44.1644712, "lon": -74.3818805, "image": get_waterbody_image(44.1644712, -74.3818805)}

    #x = __db_waterbodies.insert_one(mydict)

    #print(x.inserted_id)

    #print(__dbclient.list_database_names())

    #print( __db_waterbodies.find_one({"lat": 44.1644712, "lon": -74.3818805}) )
    #get_waterbody_image(44.1644712, -74.3818805)
