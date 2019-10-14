from genetic_algorithm import GA
from individual import Individual
from network import BiNetwork, GeoNode, Edge
from solution_generator import SolutionGenerator
from random import shuffle, randint, sample
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

#places = ['Rauðisandur', 'Hornstrandir', 'Egilsstaðir']
#places = ['Rauðisandur', 'Hornstrandir', 'Varmahlíð', 'Ásbyrgi', 'Djúpivogur', 'Svartifoss', 'Landmannalaugar', 'Hvolsvöllur', 'Geysir', 'Selfoss', 'Þríhnjúkagígur', 'Reykjavík', 'Laugavegur', 'Laugardalslaug', 'Perlan', 'Kirkjufell']
#places = ['Húsavík', 'Krafla', 'Dimmuborgir', 'Ásbyrgi', 'Þingvellir', 'Egilsstaðir', 'Þórsmörk', 'Reyðarfjörður', 'Laugarbakki', 'Akureyrarkirkja', 'Þríhnjúkagígur', 'Djúpalón', 'Fáskrúðsfjörður', 'Seljalandsfoss', 'Reynisfjara', 'Hella', 'Reykjahlíð', 'Viðey', 'Reykjavík', 'Akureyri', 'Perlan', 'Dynjandi', 'National Museum of Iceland', 'Landmannalaugar', 'Blue Lagoon', 'Hið íslenzka reðasafn', 'Mývatn', 'Rauðisandur', 'Lystigarðurinn', 'Hallgrímskirkja']
places = ['Breiðdalsvík', 'Hornstrandir', 'Hvolsvöllur', 'Hið íslenzka reðasafn', 'Lystigarðurinn', 'Skógafoss', 'Dimmuborgir', 'Djúpivogur', 'Svartifoss', 'Askja', 'Egilsstaðir', 'Grundartangi', 'Húsavík', 'Borgarnes', 'Þórsmörk', 'Selfoss', 'Alþingishúsið', 'Reykjahlíð', 'Reykjavík', 'Kirkjubæjarklaustur', 'Hallgrímskirkja', 'Blue Lagoon', 'Hella', 'Jökulsárlón', 'Fáskrúðsfjörður', 'Þingvellir', 'Laugavegur', 'Laugarbakki', 'Rauðisandur', 'Varmahlíð', 'Akureyri', 'Ásbyrgi', 'Blönduós', 'Akureyrarkirkja', 'Reyðarfjörður', 'Dynjandi', 'Seljalandsfoss', 'Harpan', 'Gullfoss', 'Dettifoss', 'Mývatn', 'Mosfellsbær', 'Viðey', 'Geysir', 'Reynisfjara', 'Perlan', 'Krafla', 'Kirkjufell', 'Landmannalaugar', 'Vík']
#2. Initialize generator
solution_generator = SolutionGenerator(places, nw, flying = True)


#Initialize crossover and mutate operators, aswell as fitness function
def fitness_func(self, network):
	'''
	This is just a test, only driving networks where enabled when this was written
	'''

	res = 0
	for i in range(0, len(self.genes)-1):
		node_from = network.get_decoded_node_with_encoded_name(self.genes[i][0])
		node_to   = network.get_decoded_node_with_encoded_name(self.genes[i+1][0])

		if self.genes[i][1] == SolutionGenerator.FLY:
			res += network.flying_cost(node_from, node_to)[0]
		else:
			res += network.shortest_path_cost(node_from, node_to)

	return 1.0/res #1/res since we a minimizing

def crossover_op(self, other, network):
	'''
	Modified crossover 5.2.1 Potvin
	'''
	assert len(self.genes) == len(other.genes) #sanity check

	flying_map = {}
	for g in self.genes:
		flying_map[g[0]] = (g[1] == SolutionGenerator.FLY)
	for g in other.genes:
		flying_map[g[0]] = flying_map[g[0]] or (g[1] == SolutionGenerator.FLY)

	crossover_point = randint(0, len(self.genes)-1)

	offspring = self.genes[:crossover_point]
	p1_set    = set([x[0] for x in offspring]) #Just a bit of optimization

	for gene in other.genes:
		if gene[0] not in p1_set:
			offspring.append((gene[0], flying_map[gene[0]]))

	assert len(self.genes) == len(offspring) #sanity check
	return Individual(offspring, network)

def create_edge_map(self, other, remaining, network):

	edge_map = {x : set() for x in remaining}
	

	assert len(self.genes) == len(other.genes) #sanity check

	for i in range(len(self.genes)):
		if self.genes[i][0] in remaining:
			for x in [-1, 1]:
				adjacent_city = self.genes[(i + x) % len(self.genes)]
				if adjacent_city[0] in remaining:
					edge_map[self.genes[i][0]].add(adjacent_city[0])
		if other.genes[i][0] in remaining:
			for x in [-1, 1]:
				adjacent_city = other.genes[(i + x) % len(other.genes)]
				if adjacent_city[0] in remaining:
					edge_map[other.genes[i][0]].add(adjacent_city[0])
	return edge_map

def crossover_op_edge_k(self, other, network):
	'''
	Potvin Edge REcombination Crossover (5.2)
	'''

	remaining = set([x[0] for x in self.genes])

	offspring = []

	flying_map = {}

	for g in self.genes:
		flying_map[g[0]] = (g[1] == SolutionGenerator.FLY)
	for g in other.genes:
		flying_map[g[0]] = flying_map[g[0]] or (g[1] == SolutionGenerator.FLY)

	selection = [self.genes[0][0], other.genes[0][0]][randint(0,1)]
	edge_map = create_edge_map(self, other, remaining, network)
	while True:
		offspring.append((selection, flying_map[selection]))
		

		
		candidates = set(edge_map[selection])

		remaining.remove(selection)
		if len(remaining) == 0: break
		for key in edge_map:
			if selection in edge_map[key]:
				edge_map[key].remove(selection) #Remove selected from candidates
		
		if len(candidates) == 0:
			selection = sample(remaining, 1)[0]
			continue

		mn_edge = min([len(edge_map[x]) for x in candidates])

		candidates = [x for x in candidates if len(edge_map[x]) == mn_edge] #reduce candidates

		selection = candidates[randint(0, len(candidates)-1)]

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

	if Individual.budget != None and randint(0, 1000) < 10: #10% chance of flipping drive to fly or fly to drive on a single gene
		i = randint(0, len(self.genes) -1)
		
		if self.genes[i] == SolutionGenerator.FLY:
			self.genes[i] = (self.genes[i][0], SolutionGenerator.DRIVE)
		else:
			self.genes[i] = (self.genes[i][0], SolutionGenerator.FLY)
		self.used_budget = self.all_used_budget(network)
		self.reduce(network)
		self.__fitness = self.fitness(network)

#Setup genetic algorithm
Individual.budget = 50000

ga = GA(crossover_op, mutate_op, fitness_func, solution_generator, 1000, nw, elitism=1)


#print(nw.shortest_path_cost_bf(askja, reykjavik))

for data in ga.evolve(2000):
	for key in data:
		print('{0}: {1}'.format(key, data[key]))

print('Used budget: ', ga.best_found.used_budget, 'Budget left: ', Individual.budget - ga.best_found.used_budget)


enc_path = nw.greedy(places, encoded = True)

#enc_path = nw.exact(places)

exact_path = [(x, 0) for x in enc_path]

visualize_with_path(nw, ga.best().genes)
#visualize_with_path(nw, exact_path)


print(nw.length_of_encoded_path(enc_path))
#print([(nw.get_decoded_node_name_with_encoded_name(x), y) for (x,y) in ga.best().genes])