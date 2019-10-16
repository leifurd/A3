import googlemaps
import math
from datetime import datetime
from random import randint, shuffle
import os
from collections import defaultdict

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

class GeoCode:
    def __init__(self):
        #Feel free to do many api calls
        self.gmaps = googlemaps.Client(key='AIzaSyAJ9TIsHsrGbw_b_ZbqN6M2xDKdACyYXxs')


    def __to_xy(self, point):
        world_coord =  self.project(point[0], point[1])

        return (world_coord[0], -world_coord[1])


    def project(self, lat, lng):
        TILE_SIZE = 1024
        siny = math.sin(lat * math.pi / 180)

        siny = min(max(siny, -0.9999), 0.9999)

        return (TILE_SIZE * (0.5 + lng / 360),
            TILE_SIZE * (0.5 - math.log((1 + siny) / (1 - siny)) / (4 * math.pi)))
      

    def get_xy_coordinates(self, place):
        geocode_result = self.gmaps.geocode(place)
        lat, lng = geocode_result[0]['geometry']['location']['lat'], geocode_result[0]['geometry']['location']['lng']

        return self.__to_xy((lat, lng))


    def get_directions(self, place_from, place_to):
        now = datetime.now()
        directions_result = self.gmaps.directions(place_from,
                                            place_to,
                                            mode="driving",
                                            departure_time=now)

        return directions_result


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


def create_randomish_edges(nodes):

    #Creates not entirely random edges
    

    shuffle(nodes)
    edge_map = defaultdict(lambda : defaultdict(int))
    dist = lambda x0, y0, x1, y1 : ((x0 - x1)**2 + (y0 - y1)**2)**0.5 
    for node in nodes:

        edges = randint(2, 5)

        x, y = node[2]

        ordered_nodes = sorted(nodes, key = lambda n : dist(n[2][0], n[2][1], x, y)) #sort by closest

        for ordered_node in ordered_nodes:
            
            if ordered_node[0] not in edge_map[node[0]] and ordered_node[0] != node[0]:
                d = dist(ordered_node[2][0], ordered_node[2][1], x, y)
                edge_map[node[0]][ordered_node[0]] = d
                edge_map[ordered_node[0]][node[0]] = d
                edges -=1

            if edges <= 0:
                break

    return edge_map


model_name = input("Insert name of model: ")

geo = GeoCode()

remove_para = lambda place : '' if place == '' or place[0] == '(' else place[0] + remove_para(place[1:])

with open('places', 'r') as f:
    places = [remove_para(x).strip() for x in f.readlines()]

failures = 0
with open('{0}.nodes'.format(model_name), 'w') as f:
    f.write('NodeName, NodeType, xy-coord, NodeCost\n')
    for place in places:
        loc = geo.get_xy_coordinates(place)

        try:
            name, location = place.split(',')
            cost = randint(1000, 25000)
            cost = (cost//1000)*1000

            f.write('{0};{1};{2};{3}\n'.format(name, 'Tourist Attraction', loc, cost))
        except:
            failures+=1
print("Failures: {0}".format(failures))


geo = GeoCode()

#geo.get_xy_coordinates('Hallgrímskirkja, Iceland')

edges = create_randomish_edges(get_nodes(model_name))

with open('{0}.edges'.format(model_name), 'w') as f:
    for place_from in edges:
        for place_to in edges[place_from]:
            f.write('{0}--{1};{2}\n'.format(place_from, place_to, edges[place_from][place_to]))