from collections import defaultdict
from heapq import heappop, heappush
from math import inf
from itertools import combinations
import plotly.graph_objects as go
import networkx as nx

import sys
sys.path.append('models')

from geo import get_edges, get_nodes

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
        

    def adjacency(self):
        for key in self.V:
            yield (key, self.__network[key])
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

    def __shortest_path_cost(self, node_from, node_to):
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
                    
        return -1

    def __floyd_warshall(self, i, j, k):
        '''
        Computes all pairs shortest path
        '''
        if self.__fw_map[i][j] != None:
            return self.__fw_map[i][j]
        if (k == 0):
            if j in self.__network_cost[i]:
                self.__fw_map[i][j] = self.__network_cost[i][j]
            else:
                self.__fw_map[i][j] = inf
        else:
            self.__fw_map[i][j] = min(self.__floyd_warshall(i, j, k-1), 
                                         self.__floyd_warshall(i, self.V[k], k-1) + self.__floyd_warshall(self.V[k], j, k-1))

        return self.__fw_map[i][j]

    def _floyd_warshall(self):
        self.__fw_map = defaultdict(lambda : defaultdict(int))
        for node_from in self.V:
            for node_to in self.V:
                self.__fw_map[node_from][node_to] = None

        for node_from in self.V:
            for node_to in self.V:
                self.__floyd_warshall(node_from, node_to, len(self.V)-1)





    def complete_transform(self):
        '''
        Transforms network into complete graph s.t. if there is no edge between A and C we will
        add the from A to C with cost of shortest path from A to C. It is enough to work for bidirectional graphs only.
        Returns the transformed network
        '''

        self._floyd_warshall()

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



def visualize(G):
    edge_x = []
    edge_y = []
    for edge in G.E:
        x0, y0 = edge.node_from.x, edge.node_from.y #G.node[edge[0]]['pos']
        x1, y1 = edge.node_to.x, edge.node_to.y #G.node[edge[1]]['pos']
        edge_x.append(x0)
        edge_x.append(x1)
        edge_x.append(None)
        edge_y.append(y0)
        edge_y.append(y1)
        edge_y.append(None)

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines')

    node_x = []
    node_y = []
    for node in G.V:
        x, y = node.x, node.y #G.node[node]['pos']
        node_x.append(x)
        node_y.append(y)

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        hoverinfo='text',
        marker=dict(
            showscale=True,
            # colorscale options
            #'Greys' | 'YlGnBu' | 'Greens' | 'YlOrRd' | 'Bluered' | 'RdBu' |
            #'Reds' | 'Blues' | 'Picnic' | 'Rainbow' | 'Portland' | 'Jet' |
            #'Hot' | 'Blackbody' | 'Earth' | 'Electric' | 'Viridis' |
            colorscale='YlGnBu',
            reversescale=True,
            color=[],
            size=10,
            colorbar=dict(
                thickness=15,
                title='Node Connections',
                xanchor='left',
                titleside='right'
            ),
            line_width=2))

    node_adjacencies = []
    node_text = []
    for node, adjacencies in G.adjacency():
        node_adjacencies.append(len(adjacencies))
        node_text.append('# of connections: '+str(len(adjacencies)) + "\nName: " + str(node))

    node_trace.marker.color = node_adjacencies
    node_trace.text = node_text


    fig = go.Figure(data=[edge_trace, node_trace],
            layout=go.Layout(
            title='<br>Network graph made with Python',
            titlefont_size=16,
            showlegend=False,
            hovermode='closest',
            margin=dict(b=20,l=5,r=5,t=40),
            annotations=[ dict(
                text="Python code: <a href='https://plot.ly/ipython-notebooks/network-graphs/'> https://plot.ly/ipython-notebooks/network-graphs/</a>",
                showarrow=False,
                xref="paper", yref="paper",
                x=0.005, y=-0.002 ) ],
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
            )
    fig.show()


if __name__ == '__main__':


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

    visualize(nw)
    #nw = get_random_network()



    #visualize(nw.complete_transform())
    '''
    a, b, c = GeoNode('a', -1, 0), GeoNode('b', 0, -1), GeoNode('c', 1, 0)


    e1, e2 = Edge(a, b, 2), Edge (b, c, 1)

    nw = BiNetwork([a, b, c], [e1, e2])
    '''
    


