import requests, os.path

API_KEY = "AIzaSyDp-d2D-ksHoMtxUYMSagJgicSW5-dVGGQ"


def get_google_sat_image(lat, long):
    lat = str(lat)
    long = str(long)
    src = "https://maps.googleapis.com/maps/api/staticmap?center=" + lat + "," + long + "&zoom=14&scale=1&format=jpg-baseline&size=639x639&style=element:label|geometry.stroke|visibility:off&style=feature:road|visibility:off&style=feature:administrative|visibility:off&style=feature:poi|visibility:off&style=feature:water|saturation:-100|invert_lightness:true&style=feature|element:labels|visibility:off"
    src = src + "&key=" + API_KEY
    dir_path = os.path.dirname(os.path.realpath(__file__))
    dest_folder = dir_path + '/satelliteImages/'
    image_name = 'google-map_' + lat + '_' + long + '.jpg'
    image_path = dest_folder + image_name

    response = requests.get(src)
    if response.status_code == 200:
        with open(image_path, 'wb') as f:
            f.write(response.content)
        return 0

    else:
        return -404

if __name__ == "__main__":
    get_google_sat_image(20.123,23.213)