from collections import defaultdict
from heapq import heappop, heappush
from math import inf
from itertools import combinations
from visualize import visualize
import networkx as nx



class Node:
    def __init__(self, name):
        self.name = name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name

    def __str__(self):
        return str(self.name)

class GeoNode(Node):
    def __init__(self, name, x, y):
        self.x = x
        self.y = y

        super().__init__(name)

class Edge:
    def __init__(self, node_from, node_to, cost):
        self.node_from = node_from
        self.node_to   = node_to
        self.cost      = cost

class BiNetwork:
    def __init__(self, vertices, edges):
        self.V                              = vertices
        self.E                              = edges
        self.__fw_map                       = None 
        self.__network, self.__network_cost = self.__initialize_network(edges)
        self.encode_map, self.decode_map    = self.__create_maps()
        self._floyd_warshall()
        

    def adjacency(self):
        for key in self.V:
            yield (key, self.__network[key])

    def __create_maps(self):
        enc_map, dec_map = {}, {}

        for idx, node in enumerate(self.V):
            enc_map[node.name] = idx
            dec_map[idx]       = node

        return (enc_map, dec_map)

    def get_encoded_node_with_name(self, node_name):
        return self.encode_map[node_name]

    def get_encoded_node_with_node(self, node):
        return self.encode_map[node.name]

    def get_decoded_node_with_encoded_name(self, encoded_name):
        
        return self.decode_map[encoded_name]

    def get_decoded_node_name_with_encoded_name(self, encoded_name):
        return self.decode_map[encoded_name].name

    def __initialize_network(self, edges):
        '''
        Assumes that A->A exists and has cost of 0
        '''
        
        n_mp = defaultdict(set)
        c_mp = defaultdict(dict)

        for edge in edges:
            n_mp[edge.node_from].add(edge.node_to)
            c_mp[edge.node_from][edge.node_to] = edge.cost
 
            n_mp[edge.node_to].add(edge.node_from)
            c_mp[edge.node_to][edge.node_from] = edge.cost

        for node in self.V:
            n_mp[node].add(node)
            c_mp[node][node] = 0

        return (n_mp, c_mp)

    def shortest_path_cost(self, node_from, node_to):
        return self.__fw_map[node_from][node_to]

    def shortest_path_cost_bf(self, node_from, node_to):
        '''
        Regular Dijkstra, used to assert fw algorithm
        '''
        pq   = []
        seen = set()

        heappush(pq, (0, node_from))

        while len(pq) > 0:

            cost, node = heappop(pq)
            seen.add(node)
            if node == node_to:
                return cost

            for neighbour in self.__network[node]:
                if neighbour not in seen:
                    heappush(pq, (cost + self.__network_cost[node][neighbour], neighbour))
                    
        return inf

    def _floyd_warshall(self):
        self.__fw_map = defaultdict(lambda : defaultdict(int))

        for i in self.V:
            for j in self.V:
                self.__fw_map[i][j] = inf

        for edge in self.E:
            self.__fw_map[edge.node_from][edge.node_to] = edge.cost
            self.__fw_map[edge.node_to][edge.node_from] = edge.cost

        for node in self.V:
            self.__fw_map[node][node] = 0

        for k in self.V:
            for i in self.V:
                for j in self.V:
                    if self.__fw_map[i][j] > self.__fw_map[i][k] + self.__fw_map[k][j]:
                        self.__fw_map[i][j] = self.__fw_map[i][k] + self.__fw_map[k][j]


    def complete_transform(self):
        '''
        Transforms network into complete graph s.t. if there is no edge between A and C we will
        add the from A to C with cost of shortest path from A to C. It is enough to work for bidirectional graphs only.
        Returns the transformed network
        '''

        edges = []

        for (node_from, node_to) in combinations(self.V, 2):
            edges.append(Edge(node_from, node_to, self.shortest_path_cost(node_from, node_to)))

        return BiNetwork(self.V, edges)



def get_random_network():
    G = nx.random_geometric_graph(200, 0.125)

    V = []
    E = []

    dist = lambda x0, y0, x1, y1 : ((x1 - x0)**2 + (y1 - y0)**2)**0.5

    for node in G.nodes():
        x, y = G.node[node]['pos']
        V.append(GeoNode(node, x, y))

    for edge in G.edges():
        x0, y0 = G.node[edge[0]]['pos']
        x1, y1 = G.node[edge[1]]['pos']

        E.append(Edge(V[edge[0]], V[edge[1]], dist(x0, y0, x1, y1)))

    return BiNetwork(V, E)




    


