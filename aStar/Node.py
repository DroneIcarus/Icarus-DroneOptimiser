import logging

logger = logging.getLogger(__name__)

class Node(object):
    def __init__(self, nodeId, distanceEnd, Latitude, Longitude, neighbors):
        super(Node, self).__init__()
        self.nodeId = nodeId
        self.Longitude = Longitude
        self.Latitude = Latitude
        self.distanceEnd = distanceEnd
        self.neighbors = neighbors
        self.isClose = False

    def AddNeighbor(self, neighborid, neighborcost):
        "add neighbor"
        self.neighbors.update({neighborid: neighborcost})

    def setPosition(self, distanceEnd, Longitude):
        "set distance"
        self.Longitude = Longitude
        self.Latitude = Latitude

    def setDistanceEnd(self, distanceEnd):
        "set distance"
        self.distanceEnd = distanceEnd

    def setID(self, nodeId):
        "set id"
        self.nodeId = nodeId
        self.isClose = False

    def print(self):
        logger.debug("ID: %s GPS: %f, %f  DistanceToEnd: %f  NbNeightbors: %d"%(self.nodeId, self.Latitude, self.Longitude, self.distanceEnd, len(self.neighbors)))

    def printneighbors(self):
        logger.debug("ID: %s NbNeightbors: %d"%(self.nodeId, self.neighbors))
