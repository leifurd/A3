from random import randint
from solution_generator import SolutionGenerator
import types

class Individual:
    budget = None
    def __init__(self, genes, network):
        '''
        Individuals get a gene distribution and a network to assert its fitness
        '''
        self.genes   = genes
        if Individual.budget != None:
            self.used_budget = self.all_used_budget(network)
            self.reduce(network)
            
        self.__fitness = Individual.fitness(self, network)

    

    def get_fitness(self):
        return self.__fitness 

    def fitness(self, network):
        raise Exception('Fitness function has not been injected into Individual')

    def crossover(self, other, network):
        raise Exception('Crossover operator has not been injected into Individual')

    def mutate(self, network):
        raise Exception('Mutation operator has not been injected into Individual')

    def all_used_budget(self, network):
        '''
        Calculates how much money is spent on flying
        '''
        res = 0
        for i in range(len(self.genes)-1):
            if self.genes[i][1] == SolutionGenerator.FLY:
                node_from = network.get_decoded_node_with_encoded_name(self.genes[i][0])
                node_to   = network.get_decoded_node_with_encoded_name(self.genes[i+1][0])

                res += network.flying_cost(node_from, node_to)[1]

        return res



    def reduce(self, network):
        '''
        If more budget is used than the maximum, remove the least significant flying edges
        '''

        if self.used_budget >=  self.budget:
            flying_edges = []
            for i in range(len(self.genes)-1):
                if self.genes[i][1] == SolutionGenerator.FLY:
                    node_from = network.get_decoded_node_with_encoded_name(self.genes[i][0])
                    node_to   = network.get_decoded_node_with_encoded_name(self.genes[i+1][0])

                    length, cost = network.flying_cost(node_from, node_to)
                    flying_edges.append((i, length, cost))
            
            flying_edges = sorted(flying_edges, key = lambda x : x[1])

            for edge in flying_edges:
                if self.used_budget <=  self.budget: break

                i, length, cost = edge

                self.genes[i] = (self.genes[i][0], SolutionGenerator.DRIVE)
                self.used_budget -= cost
            
            

                    


    def breed(self, other, network):
        '''
        Breeds two individuals to create two offsprings. Look at crossover functions in Potvin paper
        Each offspring should be processed with mutation operator
        '''

        offspring1 = self.crossover(other, network)
        offspring2 = other.crossover(self, network)

        offspring1.mutate(network)
        offspring2.mutate(network)
        return [offspring1, offspring2] #For now produce two offsprings (could have the same crossover point)


    