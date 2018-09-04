import sys, os.path
from aStar.Node import Node


class ItemList(object):
    def __init__(self, node):
        super(ItemList, self).__init__()
        self.nodeId = node.nodeId
        self.costEnd = node.distanceEnd
        self.costWay = 0
        self.cost = self.costWay + self.costEnd
        self.parent = None
        self.parentCloseListIndex = None

    def printItemList(self):
        print("{0} - costWay: {1} - Cost: {2}".format(self.nodeId, self.costWay, self.cost))


# Reconstruct the costless way from a list closed node/waypoint
def reconstructWay(closeList):
    current = closeList[-1]
    result = [current]
    while current.parent != None:
        current = closeList[current.parentCloseListIndex]
        result.insert(0, current)
    print("This is the way")
    for value in result:
        print(value.nodeId, value.parent, value.parentCloseListIndex, value.cost)
    pass


# Find the costless way from start to end
def aStar(allNodes):
    print("Starting aStar process...")
    openList = []
    closeList = []

    # add start_position to the queue
    openList.append(ItemList(allNodes['0']))

    # while the open list is not empty
    while len(openList) != 0:
        # pop the node with the lowest cost off the queue
        current = openList.pop(0)
        # Add the current to the closeList
        closeList.append(current)
        print("nodeid :", current.nodeId)
        allNodes[str(current.nodeId)].isClose = True
        if current.nodeId == 1:
            break
        for neighbors in allNodes[str(current.nodeId)].neighbors:
            if not allNodes[str(neighbors)].isClose:
                pass
                currentNeighbors = ItemList(allNodes[str(neighbors)])
                currentNeighbors.parent = current.nodeId
                currentNeighbors.parentCloseListIndex = len(closeList) - 1
                currentNeighbors.costWay = current.costWay + allNodes[str(neighbors)].neighbors[current.nodeId]
                currentNeighbors.cost = currentNeighbors.costWay + currentNeighbors.costEnd
                openList.append(currentNeighbors)
            # currentNeighbors.printItemList()
            pass

        # openList = sorted(openList, key=itemgetter('cost'), reverse=True)
        # l = sorted(openList, key=lambda k: k['cost'])
        openList = sorted(openList, key=lambda x: x.cost, reverse=False)

    reconstructWay(closeList)
    pass


# TODO: Change Name of the class for something more precise and create a file for the class
def node_parser():
    # Open a file
    dir_path = os.path.dirname(os.path.realpath(__file__))
    fo = open(dir_path + "/nodes.txt", "r+")
    line = fo.readline()

    lac_id = 0
    lac_hurestic = 0
    lac_neighbour_costs = 0
    lac_neighbour_id = 0
    allNodes = {}

    while (line):

        tab = line.split(",")
        node = Node(lac_id, lac_hurestic, {})
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
