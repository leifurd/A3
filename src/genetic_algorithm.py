from population import Population
from individual import Individual

from random import shuffle

class GA:
    def __init__(self, crossover, mutate, fitness, solution_generator, population_size, network = None, elitism = 0):
        #Inject function
        Individual.crossover      = crossover
        Individual.mutate         = mutate
        Individual.fitness        = fitness


        self.network         = network
        self.generation      = 0
        self.population      = Population(network, solution_generator, population_size)
        self.population_size = population_size
        self.best_found      = self.best()
        self.elitism         = elitism

        

    def __evolve(self):
        '''
        Evolves population by selecting individuals to breed
        '''

        #Select the fittest individuals
        fittest_individuals = self.population.select(self.population_size)
        shuffle(fittest_individuals)


        new_population      = self.population.get_elite(self.elitism)

        #Breed new population randomly
        for i in range(0, len(fittest_individuals)-1, 2):
            if len(new_population) >= self.population_size: break
            new_population.extend(fittest_individuals[i].breed(fittest_individuals[i+1], self.network))

        #Set current population to new population
        self.population.set_population(new_population)
        self.generation += 1
        

    def evolve(self, number_of_generations):
        '''
        TODO define epsilon for convergence
        '''
        for _ in range(number_of_generations):
            self.__evolve()

            data = {'Generation Number'      : self.generation,
                    'Population Size'        : len(self.population.population),
                    'Average Fitness'        : self.population.average_fitness,
                    'Best Tour'              : 1.0/self.best().get_fitness(),
                    'Average Length of Tour' : 1.0/self.population.average_fitness
                    }


            b = self.best()

            if b.get_fitness() > self.best_found.get_fitness():
                self.best_found = b

            yield data
            

    def best(self):
        '''
        Returns the individual with highest/lowest fitness
        '''
        return max([x for x in self.population.population], key = lambda x : x.get_fitness())