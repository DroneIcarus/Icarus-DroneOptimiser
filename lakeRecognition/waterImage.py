from helpers.GMapsHelper import get_google_maps_image


def get_waterbody_image(lat, lon):
    if get_google_maps_image(lat, lon):
        return True
    else:
        return False


if __name__ == "__main__":
    get_waterbody_image(44.1644712,-74.3818805)
