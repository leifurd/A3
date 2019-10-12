from genetic_algorithm import GA
from individual import Individual
from network import BiNetwork, GeoNode, Edge
from solution_generator import SolutionGenerator
from random import shuffle, randint
from visualize import visualize_with_path
import sys
sys.path.append('models')

from geo import get_edges, get_nodes


#Create graph
nodes    = get_nodes('iceland')
edge_map = get_edges('iceland')

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
places = ['Rauðisandur', 'Hornstrandir', 'Varmahlíð', 'Ásbyrgi', 'Djúpivogur', 'Svartifoss', 'Landmannalaugar', 'Hvolsvöllur', 'Geysir', 'Selfoss', 'Þríhnjúkagígur', 'Reykjavík', 'Laugavegur', 'Laugardalslaug', 'Perlan', 'Kirkjufell']
places = ['National Museum of Iceland', 'Djúpalón', 'Blue Lagoon', 'Mývatn', 'Þórsmörk', 'Seljalandsfoss', 'Hallgrímskirkja', 'Reykjahlíð', 'Reykjavík', 'Rauðisandur', 'Akureyri', 'Landmannalaugar', 'Þingvellir', 'Lystigarðurinn', 'Ásbyrgi', 'Akureyrarkirkja', 'Perlan', 'Fáskrúðsfjörður', 'Reyðarfjörður', 'Hið íslenzka reðasafn', 'Egilsstaðir', 'Hella', 'Reynisfjara', 'Krafla', 'Þríhnjúkagígur', 'Dimmuborgir', 'Dynjandi', 'Laugarbakki', 'Viðey', 'Húsavík']
places = ['Breiðdalsvík', 'Hornstrandir', 'Hvolsvöllur', 'Hið íslenzka reðasafn', 'Lystigarðurinn', 'Skógafoss', 'Dimmuborgir', 'Djúpivogur', 'Svartifoss', 'Askja', 'Egilsstaðir', 'Grundartangi', 'Húsavík', 'Borgarnes', 'Þórsmörk', 'Selfoss', 'Alþingishúsið', 'Reykjahlíð', 'Reykjavík', 'Kirkjubæjarklaustur', 'Hallgrímskirkja', 'Blue Lagoon', 'Hella', 'Jökulsárlón', 'Fáskrúðsfjörður', 'Þingvellir', 'Laugavegur', 'Laugarbakki', 'Rauðisandur', 'Varmahlíð', 'Akureyri', 'Ásbyrgi', 'Blönduós', 'Akureyrarkirkja', 'Reyðarfjörður', 'Dynjandi', 'Seljalandsfoss', 'Harpan', 'Gullfoss', 'Dettifoss', 'Mývatn', 'Mosfellsbær', 'Viðey', 'Geysir', 'Reynisfjara', 'Perlan', 'Krafla', 'Kirkjufell', 'Landmannalaugar', 'Vík']
#2. Initialize generator
solution_generator = SolutionGenerator(places, nw)


#Initialize crossover and mutate operators, aswell as fitness function
def fitness_func(self, network):
        '''
        This is just a test, only driving networks where enabled when this was written
        '''

        res = 0
        for i in range(0, len(self.genes)-1):
            node_from = network.get_decoded_node_with_encoded_name(self.genes[i][0])
            node_to   = network.get_decoded_node_with_encoded_name(self.genes[i+1][0])

            res += network.shortest_path_cost(node_from, node_to)
        
        return 1.0/res #1/res since we a minimizing

def crossover_op(self, other, network):
    '''
    Modified crossover 5.2.1 Potvin
    '''
    assert len(self.genes) == len(other.genes) #sanity check

    crossover_point = randint(0, len(self.genes)-1)

    offspring = self.genes[:crossover_point]
    p1_set    = set([x[0] for x in offspring]) #Just a bit of optimization

    for gene in other.genes:
        if gene[0] not in p1_set:
            offspring.append(gene)

    assert len(self.genes) == len(offspring) #sanity check

    return Individual(offspring, network)

def mutate_op(self, network):
    '''
    Mutate offspring
    The offspring only gets mutated with a certain probability
    '''
    if randint(0, 1000) < 50: #~5% chance of mutation this should be changed
        i, j = randint(0, len(self.genes)-1), randint(0, len(self.genes)-1)
        self.genes[i], self.genes[j] = self.genes[j], self.genes[i] #For now only swap order of two genes
        self.__fitness = self.fitness(network)

#Setup genetic algorithm

ga = GA(crossover_op, mutate_op, fitness_func, solution_generator, 2048, nw, elitism=1)


#print(nw.shortest_path_cost_bf(askja, reykjavik))

ga.evolve(100)

#enc_path = nw.greedy(places, encoded = True)

#enc_path = nw.exact(places)

#exact_path = [(x, 0) for x in enc_path]

visualize_with_path(nw, ga.best().genes)
#visualize_with_path(nw, exact_path)


#print(nw.length_of_encoded_path(enc_path))
#print([(nw.get_decoded_node_name_with_encoded_name(x), y) for (x,y) in ga.best().genes])