from population import Population
from individual import Individual

from random import shuffle

class GA:
    def __init__(self, crossover, mutate, fitness, solution_generator, population_size, network = None):
        #Inject function
        Individual.crossover      = crossover
        Individual.mutate         = mutate
        Individual.fitness        = fitness


        self.network         = network
        self.generation      = 0
        self.population      = Population(network, solution_generator, population_size)
        self.population_size = population_size

        

    def __evolve(self):
        '''
        Evolves population by selecting individuals to breed
        '''

        #Select the fittest individuals
        fittest_individuals = self.population.select(self.population_size)
        shuffle(fittest_individuals)
        new_population      = []

        #Breed new population randomly
        for i in range(0, len(fittest_individuals)-1, 2):
            new_population.extend(fittest_individuals[i].breed(fittest_individuals[i+1], self.network))

        #Set current population to new population
        self.population.set_population(new_population)
        self.generation += 1
        

    def evolve(self, number_of_generations):
        '''
        TODO define epsilon for convergence
        '''
        for _ in range(number_of_generations):
            print('Evolving generation {0}'.format(self.generation))
            self.__evolve()
            print('Done!')
            print('Population size: {0}'.format(len(self.population.population)))
            print('Average fitness: {0}'.format(self.population.average_fitness))
            print('Average length of tour: {0}'.format(1/self.population.average_fitness))
            print('Best tour: {0}'.format(self.best().get_fitness()))
            

    def best(self):
        '''
        Returns the individual with highest/lowest fitness
        '''
        return max([x for x in self.population.population], key = lambda x : x.get_fitness())