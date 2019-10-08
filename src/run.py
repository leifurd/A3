from genetic_algorithm import GA
from network import BiNetwork, GeoNode, Edge
from solution_generator import SolutionGenerator
from random import shuffle
import sys
sys.path.append('models')

from geo import get_edges, get_nodes


#Create graph
nodes    = get_nodes()
edge_map = get_edges()

V, E = [], []

node_map = {}
for node in nodes:
    V.append(GeoNode(node[0], node[2][0], node[2][1]))
    node_map[node[0]] = V[-1]

for place_from in edge_map:
    for place_to in edge_map[place_from]:
        E.append(Edge(node_map[place_from], node_map[place_to], edge_map[place_from][place_to]))

nw = BiNetwork(V, E)


#Setup solution generator for initial solution

#1. Pick N random nodes
N = 30

places = [x.name for x in V]
shuffle(places)
places = places[:N]

#2. Initialize generator
solution_generator = SolutionGenerator(places, nw)


#Setup genetic algorithm

ga = GA(None, solution_generator, 2048, nw)

ga.evolve(500)

print(ga.best().genes)