from math import radians, degrees, cos, sin, asin, atan, atan2, sqrt
from helpers import constants


# Ref: https://stackoverflow.com/questions/4913349/haversine-formula-in-python-bearing-and-distance-between-two-gps-points
# Calculate the great circle distance between two points on the earth (specified in decimal degrees)
def distBetweenCoord(lat1, long1, lat2, long2):
    # convert decimal degrees to radians
    lat1, long1, lat2, long2 = map(radians, [lat1, long1, lat2, long2])

    # haversine formula
    dlon = long2 - long1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    return c * constants.rad_earth


# Bearing is always calculated clockwise (x and y must be cartesian values)
def bearingQuadrantAngle(x, y):
    # Quadrant 1: (x+,y+)
    if x >= 0 and y >= 0:
        return 0
    # Quadrant 2: (x-,y+)
    if x < 0 and y >= 0:
        return 0
    # Quadrant 3: (x-,y-)
    if x < 0 and y < 0:
        return 180
    # Quadrant 4: (x+,y-)
    if x >= 0 and y < 0:
        return 180

# Calculates the bearing angle from North line
#   returns degrees angle
def calcBearing(x, y):

    # If y equals 0, it is whether 0*pi == 0 deg or pi == 180 deg
    if x >= 0 and y == 0:
        return 0
    elif x < 0 and y == 0:
        return 180
    else:
        return degrees(atan(x / y)) + bearingQuadrantAngle(x, y)

def calcVectorDegree(lat1, long1, lat2, long2):
    y = sin(long2-long1) * cos(lat2)
    x = cos(lat1)*sin(lat2) - sin(lat1)*cos(lat2)*cos(long2-long1)
    brng = degrees(atan2(y, x))
    return brng

#http://meteorologytraining.tpub.com/14269/css/14269_55.htm
def calcMetereologicalDegree(lat1, long1, lat2, long2):
    brng = calcVectorDegree(lat1, long1, lat2, long2)
    return 180 - brng
# Calculates a new coordinate based on start coordinates, distance and bearing
# @param $start array - start coordinate as lat/lon pair
# @param $dist  float - distance in kilometers
# @param $brng  float - bearing in degrees from North line
def calcGPSDestination(start, dist, brng):
    lat1 = radians(start.lat)
    lon1 = radians(start.lon)
    bearing = radians(brng)
    R = constants.rad_earth

    lat2 = asin(sin(lat1) * cos(dist / R) +
                cos(lat1) * sin(dist / R) * cos(bearing))

    lon2 = lon1 + atan2(sin(bearing) * sin(dist / R) * cos(lat1),
                        cos(dist / R) - sin(lat1) * sin(lat2))

    return degrees(lat2), degrees(lon2)
