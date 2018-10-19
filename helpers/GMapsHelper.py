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
GMAPS_STYLE_ONLY_WATER = "&format=jpg-baseline&size=639x639&style=element:label|geometry.stroke|visibility:off&style=feature:road|visibility:off&style=feature:administrative|visibility:off&style=feature:poi|visibility:off&style=feature:water|saturation:-100|invert_lightness:true&style=feature|element:labels|visibility:off"

dir_path = os.path.dirname(os.path.realpath(__file__))
#GMAPS_STYLE_ONLY_WATER = "&style=feature:administrative|visibility:off&style=feature:landscape|visibility:off&style=feature:poi|visibility:off&style=feature:road|visibility:off&style=feature:transit|visibility:off&style=feature:water|element:geometry|hue:0x002bff|lightness:-78"

# Please assure that you are using a key and a secret:
# https://console.cloud.google.com/apis/api/static_maps_backend/staticmap
GMAPS_STATIC_API_KEY = config['gmaps_keys']['api']
GMAPS_STATIC_SECRETS = config['gmaps_keys']['secret']

MAX_REQUEST_TRIES = 5

Coordinate = namedtuple('Coordinate', ['lat', 'lon'])
TileCoordinate = namedtuple('TileCoordinate', ['xtile', 'ytile'])

# TODO: Change every lat lon to Coordinate!!

def latlon_to_coordinate(lat, lon):
    return Coordinate(lat, lon)

def xytile_to_tilecoordinate(xtile, ytile):
    return TileCoordinate(xtile, ytile)


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
    url = STATIC_MAP_URL + GMAPS_PARAMS.format(lat, lon, 14, 640, 640, 1,
                                               "roadmap") + GMAPS_STYLE_ONLY_WATER + "&key=" + GMAPS_STATIC_API_KEY

    # Sign the url with private key
    url = sign_url(url, GMAPS_STATIC_SECRETS)

    # Create a location to store returned image
    dest_folder = Path(config['images']['lake_folder'])
    image_name = 'google-map_' + lat + '_' + lon + '.jpg'
    image_path = dest_folder / image_name

    # Make the request and save the image
    image = gmaps_request(url)
    return image


def mercator_projection(coord, tile_size):
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
    lon_deg = tilecoord.xtile / n * 360.0 - 180.0
    lat_rad = atan(sinh(pi * (1 - 2 * tilecoord.ytile / n)))
    lat_deg = degrees(lat_rad)
    return Coordinate(lat_deg, lon_deg)


if __name__ == "__main__":
    # get_google_maps_image(44.1644712,-74.3818805)
    a = Coordinate(41.850, -87.650)
    b = latlon_to_tile(a, 20)

    c = tile_to_latlon(b, 20)

    print(c)

