from pathlib import Path
import configparser
from urllib.request import urlopen
from helpers.urlsigner import sign_url
import os

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
    response = urlopen(url)
    if image is not None:
        with open(image_path, 'wb') as f:
            f.write(response.read())
        return True
    else:
        return False


if __name__ == "__main__":
    get_google_maps_image(44.1644712,-74.3818805)