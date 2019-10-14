from collections import defaultdict
from heapq import heappop, heappush
from math import inf
from itertools import combinations, permutations
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
        self.__fly_network, self.__fly_network_cost = self.__initialize_fly_network(vertices)
        self.encode_map, self.decode_map    = self.__create_maps()
        self._floyd_warshall()
        

    def adjacency(self):
        for key in self.V:
            yield (key, self.__network[key])

    def get_distance_matrix(self, places):
        '''
        Returns the distance matrix for places (places is a list of names)
        '''

        res = []

        for p_from in places:
            line = []
            for p_to in places:
                line.append(self.shortest_path_cost_name(p_from, p_to))
            res.append(line)

        return res
        
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

    
    def length_of_encoded_path(self, path):

        res = 0
        for i in range(len(path)-1):
            node_from, t1 = self.get_decoded_node_with_encoded_name(path[i][0]), path[i][1]
            node_to, t2   = self.get_decoded_node_with_encoded_name(path[i+1][0]), path[i+1][1] 

            if t1 == 1:
                res += self.flying_cost(node_from, node_to)[0]
            else:
                res += self.shortest_path_cost(node_from, node_to)
            #res += self.shortest_path_cost(node_from, node_to)

        return res

    def __initialize_fly_network(self, vertices):
        '''
        Initializes fly network s.t. each vertice can travel to any other in a straight line
        '''

        dist = lambda x0, y0, x1, y1 : ((x0 - x1)**2 + (y0 - y1)**2)**0.5 

        n_mp = defaultdict(set)
        c_mp = defaultdict(dict)

        start_cost = 10000 #The minimum cost of flying

        for node_from in vertices:
            for node_to in vertices:
                n_mp[node_from].add(node_to)
                n_mp[node_to].add(node_from)

                '''
                Here we could say that cost will be the same if distance is short?
                '''
                cost = dist(node_from.x, node_from.y, node_to.x, node_to.y)
                c_mp[node_from][node_to] = (cost/2, start_cost + 1000*cost)
                c_mp[node_to][node_from] = (cost/2, start_cost + 1000*cost)

        return (n_mp, c_mp)

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

    def shortest_path_cost_name(self, name_from, name_to):
        '''
        Returns the shortest path from a given node name to another node name
        '''
        node_from = self.get_decoded_node_with_encoded_name(self.get_encoded_node_with_name(name_from))
        node_to   = self.get_decoded_node_with_encoded_name(self.get_encoded_node_with_name(name_to))

        return self.shortest_path_cost(node_from, node_to)

    def shortest_path_cost(self, node_from, node_to):
        return self.__fw_map[node_from][node_to]

    def flying_cost(self, node_from, node_to):
        '''
        Returns the flight distance and the cost of flying
        '''

        return self.__fly_network_cost[node_from][node_to]

    
    def shortest_path_cost_bf(self, node_from, node_to):
        '''
        Regular Dijkstra, used to assert fw algorithm
        '''
        pq   = []
        seen = set()

        heappush(pq, (0, node_from, []))


        while len(pq) > 0:

            cost, node, path = heappop(pq)
            seen.add(node)
            path = path[::] + [node]
            if node == node_to:
                return path[::-1]

            for neighbour in self.__network[node]:
                if neighbour not in seen:
                    heappush(pq, (cost + self.__network_cost[node][neighbour], neighbour, path))
                    
        return []

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

    def __greedy(self, current, places):
        '''
        Helper function for greedy. Selects the closest place to current and adds it to the path
        '''

        if len(places) == 1:
            name_to = places.pop()
            return [name_to], self.shortest_path_cost_name(current, name_to)

        min_cost  = inf
        min_place = None
        for place in places:
            cost = self.shortest_path_cost_name(current, place)

            if cost < min_cost:
                min_cost  = cost
                min_place = place

        result, cost = self.__greedy(min_place, places.symmetric_difference(set([min_place])))

        return [min_place] + result, cost + min_cost
    
    def greedy(self, places, encoded = True, budget = None):
        '''
        Gives a greedy solution to visiting all places
        If encoded is flagged, will return the encoded names of the places
        '''

        places   = set(places)
        min_cost = inf
        min_path = []
        for starting_place in places:
            result, cost = self.__greedy(starting_place, places.symmetric_difference(set([starting_place])))

            if cost < min_cost:
                min_cost = cost
                min_path = [starting_place] + result

        #if budget > 0, find largest distances in tour and fly
        if budget != None:
            tour = [(self.get_decoded_node_with_encoded_name(self.get_encoded_node_with_name(x)), 0) for x in min_path]

            
            while True:
                fly = False
                distances = []
                for i in range(len(tour) -1):
                    node_from, t1 = tour[i]
                    node_to, t2   = tour[i+1]

                    if t1 != 1:
                        distances.append((self.flying_cost(node_from, node_to), i))

                distances = sorted(distances, key = lambda x : x[0][0], reverse = True)

                for (dist, cost), i in distances:
                    if cost < budget:
                        budget-= cost
                        tour[i] = (tour[i][0], 1)
                        fly = True

                if not fly:
                    break


            return [(self.get_encoded_node_with_node(x), y) for (x,y) in tour]

        return [(self.get_encoded_node_with_name(x), 0) for x in min_path]

    def exact(self, places):
        '''
        Gives exact solution to visiting all places (shortest path)
        '''

        encoded_places = [self.get_encoded_node_with_name(x) for x in places]
        
        min_cost = inf
        min_path = []
        for perm in permutations(encoded_places):
            cost = self.length_of_encoded_path(perm)

            if cost < min_cost:
                min_cost = cost
                min_path = perm

        return list(min_path)


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




    


