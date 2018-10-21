import configparser
from collections import namedtuple
from math import sin, cos, tan, atan, sinh, pi, log, degrees, radians
from urllib.request import urlopen
from helpers.urlsigner import sign_url

################### Config File ###################
config = configparser.ConfigParser()
config.read('config.ini')
# Please ensure that you are using a key and a secret:
# https://console.cloud.google.com/apis/api/static_maps_backend/staticmap
GMAPS_STATIC_API_KEY = config['gmaps_keys']['api']
GMAPS_STATIC_SECRETS = config['gmaps_keys']['secret']


################### Google Maps URL ###################
STATIC_MAP_URL = "https://maps.googleapis.com/maps/api/staticmap?"
GMAPS_PARAMS = "center={},{}&zoom={}&size={}x{}&scale={}&maptype={}"  # &format=jpg-baseline"
# Style took from https://snazzymaps.com/style/138/water-only
GMAPS_STYLE_ONLY_WATER = "&format=jpg-baseline&style=element:label|geometry.stroke|visibility:off&style=feature:road|visibility:off&style=feature:administrative|visibility:off&style=feature:poi|visibility:off&style=feature:water|saturation:-100|invert_lightness:true&style=feature|element:labels|visibility:off"
#GMAPS_STYLE_ONLY_WATER = "&style=feature:administrative|visibility:off&style=feature:landscape|visibility:off&style=feature:poi|visibility:off&style=feature:road|visibility:off&style=feature:transit|visibility:off&style=feature:water|element:geometry|hue:0x002bff|lightness:-78"


################### Coordinate tuples ###################
Coordinate = namedtuple('Coordinate', ['lat', 'lon'],)
TileCoordinate = namedtuple('TileCoordinate', ['xtile', 'ytile'])
ImagePixel = namedtuple('ImagePixel', ['x', 'y'])

################### Constants ###################
GMAPS_ZOOM = 14
GMAPS_IMAGE_SIZE_REFERENCE = ImagePixel(256, 256) # This is defined by Google Maps. NOT TO BE CHANGED.
GMAPS_IMAGE_SIZE = ImagePixel(256, 256)           # The image size we want from google maps
MAP_TILES_SIZE = TileCoordinate(2 ** GMAPS_ZOOM, 2 ** GMAPS_ZOOM)
MAX_REQUEST_TRIES = 5

# TODO: Change every lat lon to Coordinate!!
# TODO: Remove Google copyright at the bottom of map images


# Handle the Google Map request. Form the URL and sign it
def get_google_maps_image(coord):
    # Creates the URL to fetch an image
    lat = str(coord.lat)
    lon = str(coord.lon)
    url = STATIC_MAP_URL + GMAPS_PARAMS.format(lat, lon, GMAPS_ZOOM, GMAPS_IMAGE_SIZE.x, GMAPS_IMAGE_SIZE.y, 1,
                                               "roadmap") + GMAPS_STYLE_ONLY_WATER + "&key=" + GMAPS_STATIC_API_KEY

    # Sign the url with private key
    url = sign_url(url, GMAPS_STATIC_SECRETS)
    print(url)

    # Make the request and save the image
    image = gmaps_request(url)
    return image


# Make the actual request to Google Map Static API
def gmaps_request(url, try_nb=MAX_REQUEST_TRIES):
    response = urlopen(url)

    if response.status == 200:
        return response.read()

    elif response.status in range(500, 599):
        # 5xx Server Error
        # Try up to <try_nb> times
        if try_nb > 0:
            gmaps_request(url, try_nb-1)
        return None

    else:
        # For every other HTTP code... do nothing
        return None


# Convert (latitude,longitude) to a Coordinate tuple
def latlon_to_coordinate(lat, lon):
    return Coordinate(lat, lon)


# Convert (xtile, ytile) to a Tile Coordinate tuple
def xytile_to_tilecoordinate(xtile, ytile):
    return TileCoordinate(xtile, ytile)


# Return the zoom level
def get_zoom():
    return GMAPS_ZOOM


# Return the total number of tiles horizontally and vertically
def get_tile_size():
    return MAP_TILES_SIZE


# Perform the mercator projection. This is used to convert (latitude,longitude) to a point on the map
def mercator_projection(coord, tile_size=GMAPS_IMAGE_SIZE_REFERENCE):
    siny = sin(coord.lat * pi / 180)

    # Truncating to 0.9999 effectively limits latitude to 89.189.This is
    # about a third of a tile past the edge of the world tile.
    # https://developers.google.com/maps/documentation/javascript/examples/map-coordinates
    siny = min(max(siny, -0.9999), 0.9999)

    return Coordinate(tile_size.x * (0.5 + coord.lon/360),
                      tile_size.y * (0.5 - log((1 + siny) / (1 - siny)) / (4 * pi)))


def latlon_to_tile(coord, zoom):
    n = 2 ** zoom
    lat_rad = radians(coord.lat)
    xtile = int((0.5 + coord.lon/360) * n)
    ytile = int((1 - log(tan(lat_rad) + (1/cos(lat_rad))) / pi) / 2 * n)
    return TileCoordinate(xtile, ytile)


def tile_to_latlon(tilecoord, zoom):
    n = 2.0 ** zoom
    lon_deg = tilecoord.xtile  / n * 360.0 - 180.0
    lat_rad = atan(sinh(pi * (1 - 2 * tilecoord.ytile / n)))
    lat_deg = degrees(lat_rad)
    return Coordinate(lat_deg, lon_deg)


def tile_no_by_tile_coord(tile_coord, max_tile_size=MAP_TILES_SIZE):
    # Operate using Google Maps tile size of 256x256 px
    return tile_coord.xtile + tile_coord.ytile * max_tile_size.xtile


def tile_coord_by_tile_no(tile_no, max_tile_size=MAP_TILES_SIZE):
    # Operate using Google Maps tile size of 256x256 px
    ytile, xtile = divmod(tile_no, max_tile_size.xtile)
    return xytile_to_tilecoordinate(xtile, ytile)


if __name__ == "__main__":
    # NOTE: Google operates Maps using tiles of 256x256 pixels
    import cv2
    import numpy as np

    c = Coordinate(44.1644712, -74.3818805)
    b = latlon_to_tile(c, GMAPS_ZOOM)
    b1 = b._replace(xtile=b.xtile + 1)
    b2 = b._replace(xtile=b.xtile + 2)

    b = tile_to_latlon(b, GMAPS_ZOOM)
    b1 = tile_to_latlon(b1, GMAPS_ZOOM)
    b2 = tile_to_latlon(b2, GMAPS_ZOOM)

    print("{} , {}".format(b.lat, b.lon))
    print("{} , {}".format(b1.lat, b1.lon))
    print("{} , {}".format(b2.lat, b2.lon))

    c = get_google_maps_image(b)
    c1 = get_google_maps_image(b1)
    c2 = get_google_maps_image(b2)

    d = np.asarray(bytearray(c), dtype="uint8")
    d = cv2.imdecode(d, cv2.IMREAD_COLOR)
    d1 = np.asarray(bytearray(c1), dtype="uint8")
    d1 = cv2.imdecode(d1, cv2.IMREAD_COLOR)
    d2 = np.asarray(bytearray(c2), dtype="uint8")
    d2 = cv2.imdecode(d2, cv2.IMREAD_COLOR)

    cv2.imwrite('/tmp/test100.jpg', d)
    cv2.imwrite('/tmp/test101.jpg', d1)
    cv2.imwrite('/tmp/test102.jpg', d2)

