import matplotlib.pyplot as plt
from tsp_christofides import CreateGraph, DrawGraph, christofedes
import os

#main function
if __name__ == "__main__":
    G = CreateGraph()
    plt.figure(1)
    pos = DrawGraph(G,'black')
    opGraph, nodeOrder = christofedes(G, pos)
    plt.figure(2)
    pos1 = DrawGraph(opGraph,'r')
    plt.show()
    print("Order of node: ", nodeOrder)
