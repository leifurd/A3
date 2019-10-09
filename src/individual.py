from random import randint
import types

class Individual:
    def __init__(self, genes, network):
        '''
        Individuals get a gene distribution and a network to assert its fitness
        '''
        self.genes   = genes
        self.__fitness = Individual.fitness(self, network)
    

    def get_fitness(self):
        return self.__fitness 

    def fitness(self, network):
        raise Exception('Fitness function has not been injected into Individual')

    def crossover(self, other, network):
        raise Exception('Crossover operator has not been injected into Individual')

    def mutate(self, network):
        raise Exception('Mutation operator has not been injected into Individual')


    def breed(self, other, network):
        '''
        Breeds two individuals to create two offsprings. Look at crossover functions in Potvin paper
        Each offspring should be processed with mutation operator
        '''

        offspring1 = self.crossover(other, network)
        offspring2 = self.crossover(other, network)

        offspring1.mutate(network)
        offspring2.mutate(network)
        return [offspring1, offspring2] #For now produce two offsprings (could have the same crossover point)


    