from population import Population

class GA:
    def __init__(self, network = None):
        self.network    = network
        self.generation = 0
        self.population = Population(network, initial_population_size=32)

    def __evolve(self):
        '''
        Evolves population by selecting individuals to breed
        '''

        raise NotImplementedError

    def evolve(self, number_of_generations):
        for _ in range(number_of_generations):
            self.__evolve()

    def best(self):
        '''
        Returns the individual with highest/lowest fitness
        '''
        raise NotImplementedError