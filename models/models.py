from collections import defaultdict
from network import BiNetwork, GeoNode, Edge
import os

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

def get_nodes(model_name):
    with open('{0}.nodes'.format(model_name), 'r') as f:
        nodes = [x.strip() for x in f.readlines()]

    res = []
    for node in nodes[1:]:
        res.append([x.strip() for x in node.split(';')])
        res[-1][2] = eval(res[-1][2])
        #res[-1][2] = (res[-1][2][0], -res[-1][2][1])

    return res

def get_edges(model_name):
    with open('{0}.edges'.format(model_name), 'r') as f:
        edges = [x.strip() for x in f.readlines()]

    edge_map = defaultdict(lambda : defaultdict(int))

    for edge in edges:
        place_from, place_to, cost = edge.replace('--', ';').split(';')

        edge_map[place_from][place_to] = float(cost)

    return edge_map

def get_network_model(model_name):
    #Create graph
    nodes    = get_nodes(model_name)
    edge_map = get_edges(model_name)

    V, E = [], []

    node_map = {}
    for node in nodes:
        V.append(GeoNode(node[0], node[2][0], node[2][1]))
        node_map[node[0]] = V[-1]

    for place_from in edge_map:
        for place_to in edge_map[place_from]:
            E.append(Edge(node_map[place_from], node_map[place_to], edge_map[place_from][place_to]))

    nw = BiNetwork(V, E)

    return nw
