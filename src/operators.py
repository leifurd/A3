from random import randint, choice, shuffle, sample
import numpy as np
from solution_generator import SolutionGenerator
from individual import Individual


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

def crossover_MC(self, other, network):
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
  
  
def crossover_OX(self, other, network):
	'''
	Order crossover (OX) 5.2.2 Potvin
	'''
	c_point1 = randint(0, len(self.genes)-2)
	c_point2 = randint(c_point1+1, len(self.genes))

	offspring = [None]*len(self.genes)
	p1_set = {}
	for i in range(c_point1, c_point2):
		p1_set[self.genes[i][0]] = 0

	offspring[c_point1:c_point2] = self.genes[c_point1:c_point2]

	ins = c_point2
	for i in range(c_point2, c_point2 + len(self.genes)):
		idx = i % len(self.genes)
		if other.genes[idx][0] not in p1_set:
			offspring[ins % len(self.genes)] = other.genes[idx]
			ins +=1
	return Individual(offspring, network)

def crossover_OBX(self, other, network):
	num = randint(0, len(self.genes) -1)
	subset = sample(range(0, len(self.genes)), num)

	p1_set = {}
	for i in range(num):
		p1_set[self.genes[subset[i]][0]] = 1

	posInOther = []
	for i in range(len(other.genes)):
		if(other.genes[i][0] in p1_set):
			posInOther.append(i)

	offspring = [None]*len(self.genes)
	#print(self.genes)
	#print(other.genes)
	for i in range(num):
		#print("pos in self", subset[i])
		#print("pos in other", posInOther[i])

		offspring[posInOther[i]] = self.genes[subset[i]]

	ins = 0
	for i in range(len(self.genes)):

		if other.genes[i][0] not in p1_set:
			while(offspring[ins] != None):
				ins+=1
			offspring[ins] = other.genes[i]
			ins += 1
			#print(offspring)
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

def crossover_EC(self, other, network):
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
  
def mutate_SW(self, network):
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
	
def mutate_SC(self, network):
	if randint(0, 1000) < 50: #~5% chance of mutation this should be changed
		# Two random point chosen
		i = randint(0, len(self.genes)-2)
		j = randint(i+1, len(self.genes)-1)
		# Old order of points
		oldOrder = self.genes[i:j]
		# New scrambled order of indexes
		newOrder = list(range(0, j-i))
		shuffle(newOrder)
		# Scrambled indexes used order genes
		for k in range(i, j):
			self.genes[k] = oldOrder[newOrder[k-i]]
		notDone = True
		for k in range(i, j):
			if Individual.budget != None and randint(0, 1000) < 50: #5% chance of flipping drive to fly or fly to drive on the scrambled genes
				notDone = True
				if self.genes[i] == SolutionGenerator.FLY:
					self.genes[i] = (self.genes[i][0], SolutionGenerator.DRIVE)
				else:
					self.genes[i] = (self.genes[i][0], SolutionGenerator.FLY)
	self.used_budget = self.all_used_budget(network)
	self.reduce(network)
	self.__fitness = self.fitness(network) # Recalculate fitness of mutated individual
		
		
def mutate_LHC(self, network):
	'''
	Local Hill-Climbing, 2-opt
	'''

    # Chance to change the means of travel for some gene
	if Individual.budget != None and randint(0, 100) < 10: #10% chance
	    i = randint(0, len(self.genes) -1)

	    if self.genes[i] == SolutionGenerator.FLY:
	    	self.genes[i] = (self.genes[i][0], SolutionGenerator.DRIVE)
	    else:
		    self.genes[i] = (self.genes[i][0], SolutionGenerator.FLY)
	    self.used_budget = self.all_used_budget(network)
	    self.reduce(network)
	    self.__fitness = self.fitness(network)

	# Chance to mutate via local hill climbing
	if randint(0, 100) < 5: # 5% chance
		maxiters = 100 # Max iterations, iterations rarely go above 10
		iters = 0
		improved = True
		best = self # initial best sequence
		size = len(best.genes)
	
		while improved and iters < maxiters:
			improved = False
			for i in range(0, size-3):
				for j in range(i+1, size):

					# New individual created, genes swapped
					newGuy = Individual(best.genes[:], network)
					newGuy.genes[i], newGuy.genes[j] = newGuy.genes[j], newGuy.genes[i] 
					
					# Calculate the gain 
					gain = newGuy.fitness(network) - best.fitness(network)
					
					if gain > 0: 
						best = newGuy
						improved = True
						break # return to while
				else:
					break
			iters += 1
			  
		# Genes are set to new local optima
		self.genes = best.genes
		
		self.__fitness = self.fitness(network)