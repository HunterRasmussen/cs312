#!/usr/bin/python3


from CS312Graph import *
import time

class Node(object):
    id = -1     #id of given node
    prev = -1   #id of the node just before it in the path
    dist = 10000  #distance from source node to this node

def makeNode(id,prev,dist):
        node = Node()
        node.id = id
        node.prev = prev
        node.dist = dist
        return node

#I followed along with a tutorial on daniel Borowski fibonacci heap on github to build this
class HeapQueue:
    heapList = []
    currentSize = 0

    def __init__(self):
        self.heapList = [0]
        self.currentSize = 0

    def bubbleUp(self,i):
        while i//2 > 0:
            if self.heapList[i].dist < self.heapList[i//2].dist:
                temp = self.heapList[i//2]
                self.heapList[i//2] = self.heapList[i]
                self.heapList[i] = temp
            i = i//2

    def insert(self,node):
        self.heapList.append(k)
        self.currentSize +=1
        self.bubbleUp(self.currentSize)


    def bubbleDown(self, i):
        while(i*2) <= self.currentSize:
            smallestChild = self.minChild(i)
            if(self.heapList[i].dist >self.heapList[smallestChild].dist):
                temp = self.heapList[i]
                self.heapList[i] = self.heapList[smallestChild]
                self.heapList[smallestChild] = temp
            i = smallestChild

    def minChild(self,i):
        if i*2 +1 > self.currentSize:
            return i*2
        else:
            if self.heapList[i*2].dist < self.heapList[i*2+1].dist:
                return i*2
            else:
                return i*2+1

    def deleteMin(self):
        toReturn = self.heapList[1]
        self.heapList[1] = self.heapList[self.currentSize]
        self.currentSize = self.currentSize -1;
        self.heapList.pop()
        self.bubbleDown(1)
        return toReturn

    def decreaseKey(node,newDistance):
        currentNode = self.heapList[1]

class ArrayQueue:
    listOfNodes = []

    def insert(self,node):
        self.listOfNodes.append(node)

    def deleteMin(self):
        min = 10000
        toReturn = self.listOfNodes[0]
        for i in self.listOfNodes:
            if i.dist < min:
                min = i.dist
                toReturn = i
        #end for loop
        self.listOfNodes.remove(toReturn)
        return toReturn


    def decreaseKey(self,index,newDistance):
        self.listOfNodes[index].dist = newDistance


class NetworkRoutingSolver:
    def __init__( self):
        pass

    def initializeNetwork( self, network ):
        assert( type(network) == CS312Graph )
        self.network = network

    def getShortestPath( self, destIndex ):
        self.dest = destIndex
        # TODO: RETURN THE SHORTEST PATH FOR destIndex
        #       INSTEAD OF THE DUMMY SET OF EDGES BELOW
        #       IT'S JUST AN EXAMPLE OF THE FORMAT YOU'LL
        #       NEED TO USE
        path_edges = []
        total_length = 0
        startNode = self.network.nodes[self.source]
        shortestPaths = self.dijkstraPaths
        notFound = True
        currentNode = -1
        #grab the ending node
        for node in self.network.nodes:
            if node.node_id == destIndex:
                currentNode = node
        if currentNode == -1:
            return {'cost':"uncreacheable", 'path':path_edges}
        #temp prviousNode
        previousNode = ""
        while notFound: #work backwards until at the start node
            for i in shortestPaths:
                if currentNode.node_id == i.id:
                    total_length += i.dist
                    #grab the previousNode (i.e. the next node to jump to)
                    for node in self.network.nodes:
                        if node.node_id == i.prev:
                            previousNode = node
                    #get edge
                    edgeToAdd = -1
                    for edge in previousNode.neighbors:
                        if edge.src == previousNode and edge.dest == currentNode:
                            edgeToAdd = edge
                    #path_edges.append( (edgeToAdd.src.loc,edge.dest.loc, '{:.0f}'.format(edge.length)))
                    path_edges.append( (currentNode.loc,previousNode.loc, '{:.0f}'.format(edgeToAdd.length)) )
                    if previousNode == startNode:
                        notFound = False
                    else:
                        currentNode = previousNode

        #path_edges = []
        #total_length = 0
        #node = self.network.nodes[self.source]
        #edges_left = 3
        #while edges_left > 0:
        #    edge = node.neighbors[2]
        #    path_edges.append( (edge.src.loc, edge.dest.loc, '{:.0f}'.format(edge.length)) )
        #    total_length += edge.length
        #    node = edge.dest
        #    edges_left -= 1
        return {'cost':total_length, 'path':path_edges}

    def computeShortestPaths( self, srcIndex, use_heap=False ):
        self.source = srcIndex
        #y = dir(self.network)
        #print(y)
        #l = dir(self.network.nodes[1])
        #print(l)
        #print((self.network.nodes[1].loc.x()))
        #self.network.nodes[1].addEdge(4,400);
        #z = dir(self.network.nodes[1]);
        t1 = time.time()
        listOfNodes = []        #lst to keep distances and previous
        if use_heap == False:
            distanceArray = []
            unvisitedNodes = ArrayQueue()
            unvisitedNodes.listOfNodes = []
            for i in range(len(self.network.nodes)-1):
                temp = self.network.nodes[i]
                if temp.node_id == srcIndex:
                    node = makeNode(temp.node_id,temp.node_id,0)
                    unvisitedNodes.insert(node)
                    distanceArray.append(node)

                else:
                    node = makeNode(temp.node_id,-1,10000);
                    unvisitedNodes.insert(node)
                    distanceArray.append(node)

            while len(unvisitedNodes.listOfNodes) > 0:
                #grab the smallest distanced node
                currentKey = unvisitedNodes.deleteMin()

                graphNode = self.network.nodes[currentKey.id]
                for i in graphNode.neighbors:
                    newdist = currentKey.dist + i.length
                    #the node
                    distanceNodeIndex = -1
                    for j in range(len(distanceArray)-1):
                        if i.dest.node_id == distanceArray[j].id:
                            distanceNodeIndex = j;
                    if newdist < distanceArray[distanceNodeIndex].dist:
                        distanceArray[distanceNodeIndex].dist = newdist
                        distanceArray[distanceNodeIndex].prev = i.src.node_id
                        for j  in range(len(unvisitedNodes.listOfNodes)-1):
                            if unvisitedNodes.listOfNodes[j].id == i.dest.node_id:
                                unvisitedNodes.decreaseKey(j,newdist)
            self.dijkstraPaths = distanceArray;


        t2 = time.time()
        return (t2-t1)
