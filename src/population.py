from individual import Individual
import numpy as np

class Population:
    def __init__(self, network, solution_generator, initial_population_size = 32):
        self.solution_generator = solution_generator
        self.network            = network
        self.population         = self.__initialize_population(initial_population_size) #generation 0
        self.average_fitness    = self.__average_fitness()

    def __initialize_population(self, initial_population_size):
        return [Individual(self.solution_generator.get_random_encoded_solution(), self.network) for _ in range(initial_population_size)]
    
    def __average_fitness(self):
        return sum([x.get_fitness() for x in self.population])/len(self.population)

    def set_population(self, population):
        self.population      = population
        self.average_fitness = self.__average_fitness()

    def select(self, P):
        '''
        Selects P parents from the current population via proportional selection via roulette wheel selection
        '''
        
        #Sum of the fitness of all individuals
        fitness_sum = sum([x.get_fitness() for x in self.population])

        #Probability of selecting each individual
        selection_probability = [x.get_fitness()/fitness_sum for x in self.population]

        #Sample P indivduals w. replacement
        fittest_individuals = [self.population[np.random.choice(len(self.population), p=selection_probability)] for _ in range(len(self.population))]
        
        #Make sure that the list is copied
        fittest_individuals = [Individual(x.genes[:], self.network) for x in fittest_individuals]

        return fittest_individuals
