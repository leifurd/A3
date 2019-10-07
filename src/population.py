from individual import Individual

class Population:
    def __init__(self, network, initial_population_size = 32):
        self.population = self.__initialize_population(network, initial_population_size) #generation 0

    def __initialize_population(self, network, initial_population_size):
        raise NotImplementedError
    
    def set_population(self, population):
        self.population = population

    def select(self, P):
        '''
        Selects P parents from the current population via proportional selection via roulette wheel selection
        '''
        raise NotImplementedError