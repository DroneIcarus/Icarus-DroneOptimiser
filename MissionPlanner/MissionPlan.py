import sys
import os.path
import json
import csv
import logging
from shapely.geometry import Polygon
from helpers.GPSHelper import distBetweenCoord
from lakeRecognition.mapClass import Map
from lakeRecognition.lakeClass import LandingPoint


logger = logging.getLogger(__name__)

class MissionComplexItem:
    def __init__(self, item):
        self.transectStyleComplexItem = item["TransectStyleComplexItem"]
        #self.TransectStyleComplexItem.CameraCalc = self.transectStyleComplexItem['CameraCalc']
        #self.TransectStyleComplexItem.CameraTriggerInTurnAround = self.transectStyleComplexItem["CameraTriggerInTurnAround"]
        #self.TransectStyleComplexItem.FollowTerrain = self.transectStyleComplexItem["FollowTerrain"]
        #self.TransectStyleComplexItem.HoverAndCapture = self.transectStyleComplexItem["HoverAndCapture"]
        #self.TransectStyleComplexItem.FollowTerrain = self.transectStyleComplexItem["FollowTerrain"]
        #self.TransectStyleComplexItem.Items = self.transectStyleComplexItem["Items"]
        #self.TransectStyleComplexItem.Refly90Degrees = self.transectStyleComplexItem["Refly90Degrees"]
        #self.TransectStyleComplexItem.TurnAroundDistance = self.transectStyleComplexItem["TurnAroundDistance"]
        #self.TransectStyleComplexItem.VisualTransectPoints = self.transectStyleComplexItem["VisualTransectPoints"]
        self.angle = item["angle"]
        self.complexItemType = item["complexItemType"]
        self.entryLocation = item["entryLocation"]
        self.flyAlternateTransects = item["flyAlternateTransects"]
        self.polygon = item["polygon"]
        self.type = item["type"]
        self.version = item["version"]
        self.index = -1

    def get_items(self):
        item_arr = []
        for item in self.transectStyleComplexItem["Items"] :
            if item["command"] == 16 :
                newMissionItem = MissionItem(item)
                newMissionItem.set_isSurvey(True)
                newMissionItem.set_surveyIndex(self.index)
                item_arr.append(newMissionItem)
        return item_arr

    def set_items(self, items) :
        self.transectStyleComplexItem["items"] = items

    def set_index(self, index):
        self.index = index

    def get_index(self):
        return self.index

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
        self.isSurvey = False
        self.surveyIndex = -1

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
        return self.z

    def set_z(self, z):
        self.z = z

    def get_type(self):
        return self.type

    def set_type(self, type):
        self.type = type

    def get_isSurvey(self):
        return self.isSurvey

    def set_isSurvey(self, isSurvey):
        self.isSurvey = isSurvey

    def get_surveyIndex(self):
        return self.surveyIndex

    def set_surveyIndex(self, index):
        self.surveyIndex = index

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
        self.surveyItems = self.__fetch_survey_items(mission["items"])

    def get_surveyItems(self):
        return self.surveyItems

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

    # Get mission items in simple item format,
    #    the survey will only be inserted with one simple item at the beguinnig of the survey.
    def get_missionitems(self):
        missionItemList = []
        surveyPointInserted = False
        for mItem in self.missionItems:
            if(mItem.type == "SimpleItem") :
                if(mItem.command == 16 or mItem.command == 21 or mItem.command == 22) :
                    if mItem.get_isSurvey() and not surveyPointInserted :
                        missionItemList.append(mItem)
                        surveyPointInserted = True
                    elif not mItem.get_isSurvey() :
                        missionItemList.append(mItem)

        return missionItemList

    # Get mission items
    # RETURN :  Array of mission items
    def get_brut_missionitems(self):
        return self.missionItems

    # Set new mission items for the mission, will reconstruct survey(s) if needed
    # PARAMS _missionitems : Array of simple items
    def set_missionitems(self, _missionitems):
        # reconstruction des survey ..
        newMissionItems = []
        arrayOfSurvey = []
        surveyIndex = 0
        if(len(self.surveyItems) > 0):
            for newItem in _missionitems:
                if newItem.get_isSurvey() :
                    if newItem.get_surveyIndex() == surveyIndex :
                        arrayOfSurvey.append(newItem)
                    else :
                        if (len(arrayOfSurvey) != 0):
                            if (len(arrayOfSurvey) > 2):  # > 2 is the minimum for the creation of the polygon
                                newMissionItems.append(
                                    ((build_survey_mission_item(arrayOfSurvey, self.surveyItems[surveyIndex]))))
                            else:
                                logger.debug("The rest of the survey too small")
                        else :
                            arrayOfSurvey.clear()
                        arrayOfSurvey.append(newItem)
                        surveyIndex = newItem.get_surveyIndex()
                else :
                    if (len(arrayOfSurvey) != 0) : # > 2 because of creation of polygon
                        if (len(arrayOfSurvey) > 2) :
                            newMissionItems.append(
                                ((build_survey_mission_item(arrayOfSurvey, self.surveyItems[surveyIndex]))))
                        else :
                            logger.debug("The rest of the survey too small")
                        newMissionItems.append(newItem)
                        arrayOfSurvey.clear()

                    else:
                        newMissionItems.append(newItem)

            if (len(arrayOfSurvey) != 0 and len(arrayOfSurvey) > 2):  # > 2 because of creation of polygon
                newMissionItems.append(
                    ((build_survey_mission_item(arrayOfSurvey, self.surveyItems[surveyIndex]))))

        else : #modifier pour un attribu de la mission?
            logger.info("All mission simple items added")
            newMissionItems = _missionitems

        self.missionItems = newMissionItems

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

    # Get an array of waypoints, surveys are only inserted by one waypoint.
    # RETURN :  Array of [lat, lon]
    def get_waypoints(self):
        waypoints = []
        surveyPointInserted = False
        # TODO: Voir MAV_CMD au lien http://mavlink.org/messages/common
        # (Phil) Je crois qu'on devrait prend d'autres commandes que seulement 16
        #        et même jeter des execeptions quand c'est un type qui n'est pas pris en compte.
        for item in self.missionItems :
            if item.type == "SimpleItem" :
                if item.get_command() == 16 or item.get_command() == 21 or item.get_command() == 22:
                    if item.get_isSurvey() and not surveyPointInserted :
                        logger.info("Adding first survey waypoint, no other will be necessary")
                        waypoints.append(item.get_coordinate())
                        surveyPointInserted = True
                    elif not item.get_isSurvey() :
                        waypoints.append(item.get_coordinate())
                elif (item.get_command() == 17):
                    logger.error("The mission point of type 'LOITER' isn't a valid type.")
                    sys.exit("ERROR: The mission point of type 'LOITER' isn't a valid type.")
                elif (item.get_command() == 530):
                    #ToDo : Check what's 530 and add it
                    pass
                else:
                    logger.error("The mission point isn't a valid type.")
                    #sys.exit("ERROR: The mission point %d isn't a valid type."%(idx+1))

        logger.debug("Number of waypoints : " + str(len(waypoints)))
        return waypoints

    # Fetch all the mission items as simple items, surveys item will be inserted as simple items too
    # RETURN :  Array of simple mission items
    @staticmethod
    def __fetch_items(items):
        items_arr = []
        surveyIndex = 0

        for idx in range(len(items)):
            if (items[idx]["type"] == "SimpleItem") :
                items_arr.append(MissionItem(items[idx]))
            elif (items[idx]["type"] == "ComplexItem") :
                for item in items[idx]["TransectStyleComplexItem"]["Items"] :
                    surveyMissionItem = MissionItem(item)
                    surveyMissionItem.set_isSurvey(True)
                    surveyMissionItem.set_surveyIndex(surveyIndex)
                    items_arr.append(surveyMissionItem)
                surveyIndex += 1

        return items_arr

    # Fetch all the surveys of the mission
    # RETURN :  Array of complex mission items
    @staticmethod
    def __fetch_survey_items(items):
        items_arr = []
        surveyIndex = 0

        for idx in range(len(items)):
            if (items[idx]["type"] == "ComplexItem"):
                survey = MissionComplexItem(items[idx])
                survey.set_index(surveyIndex)
                items_arr.append(survey)
                surveyIndex += 1

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
        logger.info('New file is created : ' + fileName)

    def to_json(self):
        items = []
        i = 0
        for idx, item_obj in enumerate(self.mission.get_brut_missionitems()):

            if (hasattr(item_obj, 'type')) :
                if (item_obj.type == "SimpleItem"):
                    item = {
                        "autoContinue": item_obj.get_autocontinue(),
                        "command": item_obj.get_command(),
                        "doJumpId": i,
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
                    items.append(item)
                    i += 1
                elif(item_obj.type == "ComplexItem") :
                    for cItem in item_obj["TransectStyleComplexItem"]["Items"] :
                        cItem.doJumpId = i
                        i += 1
                    items.append(item_obj)
            elif (item_obj["type"] == "ComplexItem") :
                for cItem in item_obj["TransectStyleComplexItem"]["Items"]:
                    cItem["doJumpId"] = i
                    i += 1
                items.append(item_obj)


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

    # Build a simple mission item
    # PARAMS lat : latitude of the point
    # PARAMS lon : longitude of the point
    # PARAMS item_id : type of the point
    # PARAMS jumpId : the jumpId
    # RETURN : simple mission item
def build_simple_mission_item(lat, lon, item_id, jumpId=999):
    command = 16
    #alt = 50

    param1 = None
    if item_id == "start" or item_id == "takeoff":
        command = 22
    elif item_id == "wait":
        command = 93
        param1 = 3600
    elif item_id == 'charging':
        command = 21

    return {
            "autoContinue": True,
            "command": command,
            "doJumpId": jumpId,
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

    # Build a camera trigger item
    # PARAMS id : the jumpId
    # RETURN : camera trigger item
def build_camera_trigger_item(id) :
    return {
        "autoContinue": True,
        "command": 206,
        "doJumpId": id,
        "frame": 2,
        "params": [
            25,
            0,
            1,
            0,
            0,
            0,
            0
        ],
        "type": "SimpleItem"
    }

    # rebuild a similar survey complex item from the original
    # PARAMS arrayOfSimpleItems : Array of simple items to include in survey
    # PARAMS surveyItem : The original survey item to rebuild
    # RETURN : Complex survey item
def build_survey_mission_item(arrayOfSimpleItems, surveyItem) :
    points = []
    coords = []
    if(len(arrayOfSimpleItems) == 0) :
        items = []
    else :
        items = [
            build_simple_mission_item(arrayOfSimpleItems[0].get_x(), arrayOfSimpleItems[0].get_y(), "waypoint", 0),
            build_camera_trigger_item(1)
        ]
        coords.append(arrayOfSimpleItems[0].get_coordinate())
        points = [(arrayOfSimpleItems[0].get_x(), arrayOfSimpleItems[0].get_y())]

        for idx, val in enumerate(arrayOfSimpleItems):
            if(idx != 0) :
                items.append(build_simple_mission_item(val.get_x(), val.get_y(),"waypoint", idx))
                coords.append(val.get_coordinate())
                points.append((val.get_x(), val.get_y()))

    polygon = Polygon(points)
    poly = [[polygon.bounds[0],polygon.bounds[1]], [polygon.bounds[0],polygon.bounds[3]],
             [polygon.bounds[2],polygon.bounds[3]], [polygon.bounds[2],polygon.bounds[1]]]

    with open('Survey' + str(len(arrayOfSimpleItems)) + '.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerows(coords)

    return {
            "TransectStyleComplexItem": {
                "CameraCalc" : surveyItem.transectStyleComplexItem["CameraCalc"],
                "CameraTriggerInTurnAround" : surveyItem.transectStyleComplexItem["CameraTriggerInTurnAround"],
                "FollowTerrain" : surveyItem.transectStyleComplexItem["FollowTerrain"],
                "HoverAndCapture" : surveyItem.transectStyleComplexItem["HoverAndCapture"],
                "Items" : items,
                "Refly90Degrees" : surveyItem.transectStyleComplexItem["Refly90Degrees"],
                "TurnAroundDistance" : surveyItem.transectStyleComplexItem["TurnAroundDistance"],
                "VisualTransectPoints" : coords, "version" : 1,
            },
            "angle": surveyItem.angle,
            "complexItemType": surveyItem.complexItemType,
            "entryLocation": surveyItem.entryLocation,
            "flyAlternateTransects": surveyItem.flyAlternateTransects,
            "polygon": poly,
            "type": surveyItem.type,
            "version": surveyItem.version
        }