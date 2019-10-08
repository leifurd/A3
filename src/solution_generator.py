from random import shuffle, randint

class SolutionGenerator:
    DRIVE = 0
    FLY   = 1

    def __init__(self, places, network):
        self.places                      = places
        self.network                     = network


    def encode_solution(self, solution):
        '''
        Returns encoded solution, i.e. solution_i -> encode_map[solution_i]
        '''
        
        return [(self.network.get_encoded_node_with_name(x), y) for (x, y) in solution]


    def decode_solution(self, solution):
        '''
        Returns decoded solution, i.e. solution_i -> decode_map[solution_i]
        '''
        return [(self.network.get_decoded_node_name_with_encoded_name(x), y) for (x, y) in solution]

    def get_random_decoded_solution(self):
        commute = [SolutionGenerator.DRIVE]
        shuffle(self.places)

        return [x for x in zip(self.places, [commute[randint(0, len(commute)-1)] for _ in range(len(self.places))])]


    def get_random_encoded_solution(self):
        return self.encode_solution(self.get_random_decoded_solution())