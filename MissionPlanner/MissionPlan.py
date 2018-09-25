import sys
import os.path
import json
import logging
from helpers.GPSHelper import distBetweenCoord
from lakeRecognition.mapClass import Map
from lakeRecognition.lakeClass import LandingPoint


logger = logging.getLogger(__name__)


# Only deals with SimpleItem as of Feb 22nd 2018
class MissionItem:
    def __init__(self, item):
        self.autoContinue = item["autoContinue"]
        self.command = item["command"]
        self.doJumpId = item["doJumpId"]
        self.frame = item["frame"]
        self.param1 = item["params"][0]  # PARAM1
        self.param2 = item["params"][1]  # PARAM2
        self.param3 = item["params"][2]  # PARAM3
        self.param4 = item["params"][3]  # PARAM4
        self.x = item["params"][4]  # PARAM5 / local: x position, global: latitude
        self.y = item["params"][5]  # PARAM6 / y position: global: longitude
        self.z = item["params"][6]  # PARAM7 / z position: global: altitude (relative or absolute, depending on frame
        self.type = item["type"]
        self.name = None
        self.distanceEnd = 0
        self.neighbors = {}
        self.isClose = False
        self.nodeId = None
        self.landingPoint = None

    def setLandingPoint(self, landingPoint):
        if not isinstance(landingPoint, LandingPoint):
            sys.exit("Error:setLandingPoint - landingPoint is not a instance of LandingPoint")
        self.landingPoint = landingPoint

    def get_autocontinue(self):
        return self.autoContinue

    def set_autocontinue(self, autocontinue):
        self.autoContinue = autocontinue

    def get_command(self):
        return self.command

    def set_command(self, command):
        self.command = command

    def get_dojumpid(self):
        return self.doJumpId

    def set_dojumpid(self, dojumpid):
        self.doJumpId = dojumpid

    def get_frame(self):
        return self.frame

    def set_frame(self, frame):
        self.frame = frame

    def get_param1(self):
        return self.param1

    def set_param1(self, param1):
        self.param1 = param1

    def get_param2(self):
        return self.param2

    def set_param2(self, param2):
        self.param2 = param2

    def get_param3(self):
        return self.param3

    def set_param3(self, param3):
        self.param3 = param3

    def get_param4(self):
        return self.param4

    def set_param4(self, param4):
        self.param4 = param4

    def get_x(self):
        return self.x

    def set_x(self, x):
        self.x = x

    def get_y(self):
        return self.y

    def set_y(self, y):
        self.y = y

    def get_z(self):
        return self.x

    def set_z(self, z):
        self.z = z

    def get_type(self):
        return self.type

    def set_type(self, type):
        self.type = type

    def get_coordinate(self):
        return [self.x, self.y]

    def get_name(self):
        return self.name

    def set_name(self, name):
        self.name = name

    def distanceTo(self, missionItem=None, lat=None, long=None):
        if isinstance(missionItem, MissionItem):
            return distBetweenCoord(missionItem.get_x(), missionItem.get_y(),
                                    self.x, self.y)
        elif lat is not None and long is not None:
            return distBetweenCoord(lat, long,
                                    self.x, self.y)
        else:
            sys.exit("ERROR: GpsCoordinate::distanceTo() arguments are invalid...")

    def AddNeighbor(self, neighborid, neighborcost):
        "add neighbor"
        self.neighbors.update({neighborid: neighborcost})

    def setPosition(self, Latitude, Longitude):
        "set position"
        self.y = Longitude
        self.x = Latitude

    def setDistanceEnd(self, distanceEnd):
        "set distance"
        self.distanceEnd = distanceEnd

    def setID(self, nodeId):
        "set id"
        self.nodeId = nodeId
        self.isClose = False

    def getID(self):
        return self.nodeId

    def printNode(self):
        logger.debug("ID: %s GPS: %f, %f  DistanceToEnd: %f  NbNeightbors: %d"%(self.nodeId, self.x, self.y, self.distanceEnd, len(self.neighbors)))

    def printneighbors(self):
        logger.debug("ID: %s NbNeightbors: %d"%(self.nodeId, self.neighbors))

    def printGPS(self):
        logger.info("Name: %s (Latitude: %s Longitude: %s)", self.name, self.x, self.y)


# Actually only handles missions of version V2
class Mission:
    def __init__(self, mission):
        self.cruiseSpeed = mission["cruiseSpeed"]
        self.firmwareType = mission["firmwareType"]
        self.hoverSpeed = mission["hoverSpeed"]
        self.missionItems = self.__fetch_items(mission["items"])
        self.plannedHomePosition = mission["plannedHomePosition"]
        self.vehicleType = mission["vehicleType"]
        self.version = mission["version"]

    def get_cruisespeed(self):
        return self.cruiseSpeed

    def set_cruisespeed(self, cruisespeed):
        self.cruiseSpeed = cruisespeed

    def get_firmwaretype(self):
        return self.firmwareType

    def set_firmwaretype(self, firmwaretype):
        self.firmwareType = firmwaretype

    def get_hoverspeed(self):
        return self.hoverSpeed

    def set_hoverspeed(self, hoverspeed):
        self.hoverSpeed = hoverspeed

    def get_missionitems(self):
        return self.missionItems

    def set_missionitems(self, missionitems):
        self.missionItems = self.__fetch_items(missionitems)

    def set_missionitems2(self,missionitems):
        self.missionItems = missionitems

    def get_plannedhomeposition(self):
        return self.plannedHomePosition

    def set_plannedhomeposition(self, plannedhomeposition):
        self.plannedHomePosition = plannedhomeposition

    def get_vehicletype(self):
        return self.vehicleType

    def set_vehicletype(self, vehicletype):
        self.vehicleType = vehicletype

    def get_version(self):
        return self.version

    def set_version(self, version):
        self.version = version

    def get_waypoints(self):
        waypoints = []

        # TODO: Voir MAV_CMD au lien http://mavlink.org/messages/common
        # (Phil) Je crois qu'on devrait prend d'autres commandes que seulement 16
        #        et même jeter des execeptions quand c'est un type qui n'est pas pris en compte.
        for idx in range(len(self.missionItems)):
            if (self.missionItems[idx].get_command() == 16
                    or self.missionItems[idx].get_command() == 21
                    or self.missionItems[idx].get_command() == 22):
                waypoints.append(self.missionItems[idx].get_coordinate())
            elif (self.missionItems[idx].get_command() == 17):
                logger.error("The mission point %d of type 'LOITER' isn't a valid type."%(idx+1))
                sys.exit("ERROR: The mission point %d of type 'LOITER' isn't a valid type."%(idx+1))
            else:
                logger.error("The mission point %d isn't a valid type."%(idx+1))
                sys.exit("ERROR: The mission point %d isn't a valid type."%(idx+1))
        return waypoints

    @staticmethod
    def __fetch_items(items):
        items_arr = []

        for idx in range(len(items)):
            items_arr.append(MissionItem(items[idx]))

        return items_arr


# Actually only handles .plan of version V1
class MissionSettings:
    def __init__(self, json_obj):
        self.fileType = json_obj["fileType"]
        self.geoFence = json_obj["geoFence"]  # Actually doesnt have a class
        self.groundStation = json_obj["groundStation"]
        self.rallyPoints = json_obj["rallyPoints"]  # Actually doesnt have a class
        self.version = json_obj["version"]

    def get_filetype(self):
        return self.fileType

    def set_filetype(self, filetype):
        self.fileType = filetype

    def get_geofence(self):
        return self.geoFence

    # TODO: Add geofence class
    def set_geofence(self, geofence):
        self.geoFence = geofence

    def get_groundstation(self):
        return self.groundStation

    def set_groundstation(self, groundstation):
        self.groundStation = groundstation

    def get_rallyPoints(self):
        return self.rallyPoints

    def set_rallyPoints(self, rallypoints):
        self.rallyPoints = rallypoints

    def get_version(self):
        return self.version

    def set_version(self, version):
        self.version = version


class MissionPlan:
    def __init__(self, json_file):
        if os.path.isfile(json_file):
            if is_json(json_file):
                json_obj = json.load(open(json_file))
                self.missionSettings = MissionSettings(json_obj)
                self.mission = Mission(json_obj["mission"])

            else:
                raise ValueError("could not open a valid JSON file: %r" % json_file)
        else:
            raise ValueError("could not open file: %r" % json_file)

    def get_missionsettings(self):
        return self.missionSettings

    def set_missionsettings(self, missionsettings):
        self.missionSettings = missionsettings

    def get_mission(self):
        return self.mission

    def set_mission(self, mission):
        self.mission = mission

    def write_to_file(self, fileName):
        if not fileName.endswith(".plan"):
            fileName += '.plan'
        with open(fileName, 'w') as outfile:
            json.dump(self.to_json(), outfile, indent=4, sort_keys=True)
        print('New file is created !')

    def to_json(self):
        items = []

        for idx, item_obj in enumerate(self.mission.get_missionitems()):
            item = {
                "autoContinue": item_obj.get_autocontinue(),
                "command": item_obj.get_command(),
                "doJumpId": idx + 1,
                "frame": item_obj.get_frame(),
                "params": [
                    item_obj.get_param1(),
                    item_obj.get_param2(),
                    item_obj.get_param3(),
                    item_obj.get_param4(),
                    item_obj.get_x(),
                    item_obj.get_y(),
                    item_obj.get_z()
                ],
                "type": item_obj.get_type()
            }
            items.insert(len(items), item)

        return {
            "fileType": self.missionSettings.get_filetype(),
            "geoFence": self.missionSettings.get_geofence(),
            "groundStation": self.missionSettings.get_groundstation(),
            "mission": {
                "cruiseSpeed": self.mission.get_cruisespeed(),
                "firmwareType": self.mission.get_firmwaretype(),
                "hoverSpeed": self.mission.get_hoverspeed(),
                "items": items,
                "plannedHomePosition": self.mission.get_plannedhomeposition(),
                "vehicleType": self.mission.get_vehicletype(),
                "version": self.mission.get_version()
            },
            "rallyPoints": self.missionSettings.get_rallyPoints(),
            "version": self.missionSettings.get_version()
        }


def is_json(json_file):
    try:
        json.load(open(json_file))
    except ValueError as e:
        return False
    return True

def build_simple_mission_item(lat, lon, item_id):
    command = 16
    #alt = 50

    param1 = None
    if item_id == "start" or item_id == "takeoff":
        command = 22
    if item_id == "wait":
        command = 93
        param1 = 3600
    if item_id == 'charging':
        command = 21

    return {
            "autoContinue": True,
            "command": command,
            "doJumpId": 999,
            "frame": 3,
            "params": [
                param1,
                None,
                None,
                None,
                lat,
                lon,
                None
            ],
            "type": "SimpleItem"
        }
