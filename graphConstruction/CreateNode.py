import sys, os
from aStar.Node import Node
from aStar.aStar import ItemList, aStar, reconstructWay
from MissionPlanner.MissionPlan import MissionItem
from MissionPlanner.MissionPlan import build_simple_mission_item


# nodeId, distanceEnd,gpsLandingPoint, neighbors
def node_create(lakeList, missionItemStart, missionItemEnd, distanceMax):
    allNodes = {}

    # End landing point
    missionItemEnd.setID('end')
    allNodes['end'] = missionItemEnd

    # Start landing point
    missionItemStart.setID('start')
    missionItemStart.setDistanceEnd(missionItemStart.distanceTo(lat=missionItemEnd.get_x(), long=missionItemEnd.get_y()))
    allNodes['start'] = missionItemStart

    for x in range(0, len(lakeList)):
        # gpsLandingPoints = lakeList[x].getLandingPoint()
        gpsLandingPoints = lakeList[x].getSortLandingPoint(distanceMax)

        for y in range(0, len(gpsLandingPoints)):
            missionItem = MissionItem(build_simple_mission_item(gpsLandingPoints[y][0], gpsLandingPoints[y][1],'lac_id:' + str(x) + ':' + str(y)))
            missionItem.setID('lac_id:' + str(x) + ':' + str(y))
            missionItem.setDistanceEnd(
                missionItem.distanceTo(lat=missionItemEnd.get_x(), long=missionItemEnd.get_y()))
            allNodes['lac_id:' + str(x) + ':' + str(y)] = missionItem

    return allNodes

def node_set_neighbours(allNodes, distanceMin, distanceMax):
    nodes = allNodes.values()
    for node1 in nodes:
        for node2 in nodes:
            distance = node1.distanceTo(missionItem=node2)
            if (distance > distanceMin and distance < distanceMax):
                    neighbors = list(node1.neighbors.items())
                    node1.AddNeighbor(node2.nodeId, node1.distanceTo(missionItem=node2))


# TODO: Change Name of the class for something more precise and create a file for the class
def node_parser():
    # Open a file
    fo = open(os.path.dirname(__file__) + "/nodes.txt", "r+")
    line = fo.readline()

    lac_id = 0
    lac_hurestic = 0
    lac_neighbour_costs = 0
    lac_neighbour_id = 0
    allNodes = {}

    while (line):

        tab = line.split(",")
        node = Node(lac_id, lac_hurestic, 0, {})
        for x in range(0, len(tab)):
            temp1 = tab[x].split(":")
            if (temp1[0] == "Current ID"):
                lac_id = int(temp1[1])
                node.setID(lac_id)
                print("id -> %d" % (lac_id))
            elif (temp1[0] == "Huristic"):
                lac_hurestic = float(temp1[1])
                node.setDistanceEnd(lac_hurestic)
                print("hurestic -> %f" % (lac_hurestic))
            elif (temp1[0] == "neighbour"):
                lac_neighbour_id = int(temp1[1])
                print("neighbor id -> %d" % (lac_neighbour_id))
            elif (temp1[0] == "cost"):
                lac_neighbour_costs = float(temp1[1])
                print("cost -> %f" % (lac_neighbour_costs))
                node.AddNeighbor(lac_neighbour_id, lac_neighbour_costs)

        allNodes[str(lac_id)] = node
        print("node -> %s" % (lac_id))
        line = fo.readline()
    aStar(allNodes)


def main(argv):
    # FAKE DATA ############################
    node_parser()


if __name__ == "__main__":
    main(sys.argv)
