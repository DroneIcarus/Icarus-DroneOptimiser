import sys
import math as math
import logging

from aStar.Node import Node

logger = logging.getLogger(__name__)

# TODO: Change Name of the class for something more precise and create a file for the class
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
    result = [current.nodeId]
    while current.parent != None:
        current = closeList[current.parentCloseListIndex]
        result.insert(0, current.nodeId)
    # print("This is the way")
    # for value in result:
    # 	print(value.nodeId, value.parent, value.parentCloseListIndex, value.cost)
    return result


# Find the costless way from start to end
def aStar(allNodes):
    # print("Starting aStar process...")
    success = False
    result = None
    openList = []
    closeList = []

    # add start_position to the queue
    openList.append(ItemList(allNodes['start']))

    print("openList : " + str(len(openList)))
    # while the open list is not empty
    while len(openList) != 0:
        # pop the node with the lowest cost off the queue
        current = openList.pop(0)
        # Add the current to the closeList
        closeList.append(current)
        allNodes[str(current.nodeId)].isClose = True
        if current.nodeId == 'end':
            success = True
            break
        for neighbors in allNodes[str(current.nodeId)].neighbors:
            if not allNodes[str(neighbors)].isClose:
                if current.nodeId in allNodes[str(neighbors)].neighbors:
                    currentNeighbors = ItemList(allNodes[str(neighbors)])
                    currentNeighbors.parent = current.nodeId
                    currentNeighbors.parentCloseListIndex = len(closeList) - 1
                    currentNeighbors.costWay = current.costWay + allNodes[str(neighbors)].neighbors[current.nodeId]
                    currentNeighbors.cost = currentNeighbors.costWay + currentNeighbors.costEnd
                    openList.append(currentNeighbors)
            # currentNeighbors.printItemList()

        # openList = sorted(openList, key=itemgetter('cost'), reverse=True)
        # l = sorted(openList, key=lambda k: k['cost'])
        openList = sorted(openList, key=lambda x: x.cost, reverse=False)

    print("closelist")
    print(closeList)
    result = reconstructWay(closeList)
    return success, result


def main(argv):
    # FAKE DATA ############################

    start = Node("0", math.sqrt(13), 0, {"A": 1, "C": 3},None)
    a = Node("A", math.sqrt(8), 0, {"start": 1, "B": 1, "G": 1},None)
    b = Node("B", math.sqrt(5), 0, {"A": 1, "C": 1},None)
    c = Node("C", 2, 0, {"B": 1, "D": 1, "E": 1, "H": 1, "start": 3},None)
    d = Node("D", math.sqrt(5), 0, {"C": 1, "F": 1, "end": math.sqrt(5)},None)
    e = Node("E", 3, 0, {"C": 1, "F": 1},None)
    f = Node("F", math.sqrt(10), 0, {"D": 1, "E": 1},None)
    g = Node("G", math.sqrt(5), 0, {"A": 1, "I": 1},None)
    h = Node("H", 1, 0, {"C": 1, "end": 1},None)
    i = Node("I", 2, 0, {"G": 1},None)
    end = Node("1", 0, 0, {"D": math.sqrt(5), "H": 1},None)

    allNodes = {
        "start": start,
        "A": a,
        "B": b,
        "C": c,
        "D": d,
        "E": e,
        "F": f,
        "G": g,
        "H": h,
        "I": i,
        "end": end
    }
    # END FAKE DATA ############################

    aStar(allNodes)


if __name__ == "__main__":
    main(sys.argv)
