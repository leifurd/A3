from genetic_algorithm import GA
from individual import Individual
from network import BiNetwork, GeoNode, Edge
from solution_generator import SolutionGenerator
from random import shuffle, randint, sample
from visualize import visualize_with_path, draw_convergence_figure


import sys
sys.path.append('models')

from models import get_network_model

nw = get_network_model('iceland')


V, E = nw.V, nw.E
nw = BiNetwork(V, E)


#Setup solution generator for initial solution

#1. Pick N random nodes
#N = 30

#places = [x.name for x in V]
#shuffle(places)

#Or pick nodes from one of the below

#places = ['Rauðisandur', 'Hornstrandir', 'Egilsstaðir']
#places = ['Rauðisandur', 'Hornstrandir', 'Varmahlíð', 'Ásbyrgi', 'Djúpivogur', 'Svartifoss', 'Landmannalaugar', 'Hvolsvöllur', 'Geysir', 'Selfoss', 'Þríhnjúkagígur', 'Reykjavík', 'Laugavegur', 'Laugardalslaug', 'Perlan', 'Kirkjufell']
places = ['National Museum of Iceland', 'Djúpalón', 'Blue Lagoon', 'Mývatn', 'Þórsmörk', 'Seljalandsfoss', 'Hallgrímskirkja', 'Reykjahlíð', 'Reykjavík', 'Rauðisandur', 'Akureyri', 'Landmannalaugar', 'Þingvellir', 'Lystigarðurinn', 'Ásbyrgi', 'Akureyrarkirkja', 'Perlan', 'Fáskrúðsfjörður', 'Reyðarfjörður', 'Hið íslenzka reðasafn', 'Egilsstaðir', 'Hella', 'Reynisfjara', 'Krafla', 'Þríhnjúkagígur', 'Dimmuborgir', 'Dynjandi', 'Laugarbakki', 'Viðey', 'Húsavík']
#places = ['Breiðdalsvík', 'Hornstrandir', 'Hvolsvöllur', 'Hið íslenzka reðasafn', 'Lystigarðurinn', 'Skógafoss', 'Dimmuborgir', 'Djúpivogur', 'Svartifoss', 'Askja', 'Egilsstaðir', 'Grundartangi', 'Húsavík', 'Borgarnes', 'Þórsmörk', 'Selfoss', 'Alþingishúsið', 'Reykjahlíð', 'Reykjavík', 'Kirkjubæjarklaustur', 'Hallgrímskirkja', 'Blue Lagoon', 'Hella', 'Jökulsárlón', 'Fáskrúðsfjörður', 'Þingvellir', 'Laugavegur', 'Laugarbakki', 'Rauðisandur', 'Varmahlíð', 'Akureyri', 'Ásbyrgi', 'Blönduós', 'Akureyrarkirkja', 'Reyðarfjörður', 'Dynjandi', 'Seljalandsfoss', 'Harpan', 'Gullfoss', 'Dettifoss', 'Mývatn', 'Mosfellsbær', 'Viðey', 'Geysir', 'Reynisfjara', 'Perlan', 'Krafla', 'Kirkjufell', 'Landmannalaugar', 'Vík']


#2. Initialize generator
solution_generator = SolutionGenerator(places, nw, flying = True) #Tour is allowed to have flights as commute type


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

from operators import crossover_EC, crossover_MC, crossover_OX, mutate_LHC, mutate_SC, mutate_SW


#Setup genetic algorithm

budget = 50000 #Amount of icelandic krona a solution is allowed to use
generations = 1000 #Amount of generations the agorithm should evolve
intial_population = 1000 #Size of initial population

Individual.budget = budget #Set the budget for all solutions

#Pass in the crossover, mutate and fitness functions
ga = GA(crossover_MC, mutate_SW, fitness_func, solution_generator, intial_population, nw, elitism=1, budget = budget)


#Run for 
for data in ga.evolve(1000):
	for key in data:
		print('{0}: {1}'.format(key, data[key]))

print('Used budget: ', ga.best_found.used_budget, 'Budget left: ', Individual.budget - ga.best_found.used_budget)


#Compute greedy for comparison (greedy gives very nice results)
enc_path = nw.greedy(places, encoded = True, budget = 50000)

#enc_path = nw.exact(places)

#exact_path = [(x, 0) for x in enc_path]

visualize_with_path(nw, ga.best().genes)
print(1.0/ga.best().get_fitness())

#visualize_with_path(nw, enc_path)



#print(nw.length_of_encoded_path(enc_path))
#print([(nw.get_decoded_node_name_with_encoded_name(x), y) for (x,y) in ga.best().genes])