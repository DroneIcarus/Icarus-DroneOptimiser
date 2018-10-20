import os
import configparser
from collections import namedtuple
from pathlib import Path
from math import sin, cos, tan, atan, sinh, pi, log, degrees, radians
from urllib.request import urlopen
from helpers.urlsigner import sign_url

# Fetches variables from the config file
config = configparser.ConfigParser()
config.read('config.ini')

STATIC_MAP_URL = "https://maps.googleapis.com/maps/api/staticmap?"
GMAPS_PARAMS = "center={},{}&zoom={}&size={}x{}&scale={}&maptype={}"  # &format=jpg-baseline"
# Style took from https://snazzymaps.com/style/138/water-only
GMAPS_STYLE_ONLY_WATER = "&format=jpg-baseline&style=element:label|geometry.stroke|visibility:off&style=feature:road|visibility:off&style=feature:administrative|visibility:off&style=feature:poi|visibility:off&style=feature:water|saturation:-100|invert_lightness:true&style=feature|element:labels|visibility:off"

dir_path = os.path.dirname(os.path.realpath(__file__))
#GMAPS_STYLE_ONLY_WATER = "&style=feature:administrative|visibility:off&style=feature:landscape|visibility:off&style=feature:poi|visibility:off&style=feature:road|visibility:off&style=feature:transit|visibility:off&style=feature:water|element:geometry|hue:0x002bff|lightness:-78"

# Please assure that you are using a key and a secret:
# https://console.cloud.google.com/apis/api/static_maps_backend/staticmap
GMAPS_STATIC_API_KEY = config['gmaps_keys']['api']
GMAPS_STATIC_SECRETS = config['gmaps_keys']['secret']

Coordinate = namedtuple('Coordinate', ['lat', 'lon'],)
TileCoordinate = namedtuple('TileCoordinate', ['xtile', 'ytile'])

MAX_REQUEST_TRIES = 5
TILE_SIZE = TileCoordinate(512, 512)

# TODO: Change every lat lon to Coordinate!!
# TODO: Remove Google copyright at the bottom of map images


def latlon_to_coordinate(lat, lon):
    return Coordinate(lat, lon)


def xytile_to_tilecoordinate(xtile, ytile):
    return TileCoordinate(xtile, ytile)


def get_tile_size():
    return TILE_SIZE


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


def get_google_maps_image(lat, lon):
    # Creates the URL to fetch an image
    lat = str(lat)
    lon = str(lon)
    url = STATIC_MAP_URL + GMAPS_PARAMS.format(lat, lon, 14, 256, 256, 1,
                                               "roadmap") + GMAPS_STYLE_ONLY_WATER + "&key=" + GMAPS_STATIC_API_KEY

    # Sign the url with private key
    url = sign_url(url, GMAPS_STATIC_SECRETS)
    print(url)

    # Make the request and save the image
    image = gmaps_request(url)
    return image


def mercator_projection(coord, tile_size):
    siny = sin(coord.lat * pi / 180)

    # Truncating to 0.9999 effectively limits latitude to 89.189.This is
    # about a third of a tile past the edge of the world tile.
    # https://developers.google.com/maps/documentation/javascript/examples/map-coordinates
    siny = min(max(siny, -0.9999), 0.9999)

    return Coordinate(tile_size.xtile * (0.5 + coord.lon/360),
                      tile_size.ytile * (0.5 - log((1 + siny) / (1 - siny)) / (4 * pi)))


def latlon_to_tile(coord, zoom):
    n = 2 ** zoom
    lat_rad = radians(coord.lat)
    xtile = int((0.5 + coord.lon/360) * n)
    ytile = int((1 - log(tan(lat_rad) + (1/cos(lat_rad))) / pi) / 2 * n)
    return TileCoordinate(xtile, ytile)


def tile_to_latlon(tilecoord, zoom):
    n = 2.0 ** zoom
    lon_deg = tilecoord.xtile / n * 360.0 - 180.0
    lat_rad = atan(sinh(pi * (1 - 2 * tilecoord.ytile / n)))
    lat_deg = degrees(lat_rad)
    return Coordinate(lat_deg, lon_deg)


if __name__ == "__main__":
    #NOTE: Google operates Maps using tile of 256x256 pixels
    import cv2
    import numpy as np
    # get_google_maps_image(44.1644712,-74.3818805)

    # Our implementation
    a = Coordinate(44.1644712, -74.3818805)
    print(latlon_to_tile(a,14))

    # Using mercator function
    lat,lon = mercator_projection(a, TILE_SIZE)
    lat = lat * (2 ** 14)/ TILE_SIZE.xtile
    lon = lon * (2 ** 14)/ TILE_SIZE.ytile
    print("{} , {}".format(lat, lon))

    b = tile_to_latlon(TileCoordinate(4806,5947), 14)
    b1 = tile_to_latlon(TileCoordinate(4807,5947), 14)
    b2 = tile_to_latlon(TileCoordinate(4808,5947), 14)

    c = get_google_maps_image(b.lat, b.lon)
    c1 = get_google_maps_image(b1.lat, b1.lon)
    c2 = get_google_maps_image(b2.lat, b2.lon)

    d = np.asarray(bytearray(c), dtype="uint8")
    d = cv2.imdecode(d, cv2.IMREAD_COLOR)
    d1 = np.asarray(bytearray(c1), dtype="uint8")
    d1 = cv2.imdecode(d1, cv2.IMREAD_COLOR)
    d2 = np.asarray(bytearray(c2), dtype="uint8")
    d2 = cv2.imdecode(d2, cv2.IMREAD_COLOR)

    cv2.imwrite('/tmp/test.jpg', d)
    cv2.imwrite('/tmp/test1.jpg', d1)
    cv2.imwrite('/tmp/test2.jpg', d2)

