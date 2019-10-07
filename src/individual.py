
class Individual:
    def __init__(self, genes, network):
        '''
        Individuals get a gene distribution and a network to assert its fitness
        '''
        self.genes   = genes
        self.fitness = self.__fitness(genes, network)

    def __fitness(self, genes, network):
        raise NotImplementedError

    def breed(self, other):
        '''
        Breeds two individuals to create two offsprings. Look at crossover functions in Potvin paper
        Each offspring should be processed with mutation operator
        '''
        raise NotImplementedError

    def mutate(self):
        raise NotImplementedError