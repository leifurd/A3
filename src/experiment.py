from genetic_algorithm import GA
from individual import Individual
from network import BiNetwork, GeoNode, Edge
from solution_generator import SolutionGenerator
from random import shuffle, randint, sample
from visualize import visualize_with_path, draw_convergence_figure
from operators import crossover_EC, crossover_MC, crossover_OBX, crossover_OX, mutate_LHC, mutate_SC, mutate_SW, fitness_func

import time
import sys
sys.path.append('models')

from models import get_network_model

nw = get_network_model('iceland')

#places = ['Rauðisandur', 'Hornstrandir', 'Egilsstaðir']
#places = ['Rauðisandur', 'Hornstrandir', 'Varmahlíð', 'Ásbyrgi', 'Djúpivogur', 'Svartifoss', 'Landmannalaugar', 'Hvolsvöllur', 'Geysir', 'Selfoss', 'Þríhnjúkagígur', 'Reykjavík', 'Laugavegur', 'Laugardalslaug', 'Perlan', 'Kirkjufell']
places = ['National Museum of Iceland', 'Djúpalón', 'Blue Lagoon', 'Mývatn', 'Þórsmörk', 'Seljalandsfoss', 'Hallgrímskirkja', 'Reykjahlíð', 'Reykjavík', 'Rauðisandur', 'Akureyri', 'Landmannalaugar', 'Þingvellir', 'Lystigarðurinn', 'Ásbyrgi', 'Akureyrarkirkja', 'Perlan', 'Fáskrúðsfjörður', 'Reyðarfjörður', 'Hið íslenzka reðasafn', 'Egilsstaðir', 'Hella', 'Reynisfjara', 'Krafla', 'Þríhnjúkagígur', 'Dimmuborgir', 'Dynjandi', 'Laugarbakki', 'Viðey', 'Húsavík']
#places = ['Breiðdalsvík', 'Hornstrandir', 'Hvolsvöllur', 'Hið íslenzka reðasafn', 'Lystigarðurinn', 'Skógafoss', 'Dimmuborgir', 'Djúpivogur', 'Svartifoss', 'Askja', 'Egilsstaðir', 'Grundartangi', 'Húsavík', 'Borgarnes', 'Þórsmörk', 'Selfoss', 'Alþingishúsið', 'Reykjahlíð', 'Reykjavík', 'Kirkjubæjarklaustur', 'Hallgrímskirkja', 'Blue Lagoon', 'Hella', 'Jökulsárlón', 'Fáskrúðsfjörður', 'Þingvellir', 'Laugavegur', 'Laugarbakki', 'Rauðisandur', 'Varmahlíð', 'Akureyri', 'Ásbyrgi', 'Blönduós', 'Akureyrarkirkja', 'Reyðarfjörður', 'Dynjandi', 'Seljalandsfoss', 'Harpan', 'Gullfoss', 'Dettifoss', 'Mývatn', 'Mosfellsbær', 'Viðey', 'Geysir', 'Reynisfjara', 'Perlan', 'Krafla', 'Kirkjufell', 'Landmannalaugar', 'Vík']


solution_generator = SolutionGenerator(places, nw)


crossover_ops = {'MC' : crossover_MC,  'EC' : crossover_EC, 'OBX' : crossover_OBX, 'OX' : crossover_OX}
mutate_ops   = {'SW' : mutate_SW, 'SC' : mutate_SC, 'LHC' : mutate_LHC}

BUDGET = 50000
Individual.budget    = BUDGET
Individual.fitness   = fitness_func
experiment  = {'Fitness' : [], 'Cross' : [], 'Mutate' : []}
performance = {}
execution_time = {}
solutions = {}
budget_used = {}
#Compute greedy performance
start = time.time()
enc_path = nw.greedy(places, encoded = True, budget = BUDGET)
end = time.time()

performance['Greedy'] = nw.length_of_encoded_path(enc_path)
execution_time['Greedy'] = (end - start)
solutions['Greedy'] = enc_path
budget_used['Greedy'] = Individual(enc_path, nw).used_budget

left = len(crossover_ops)*len(mutate_ops)
generations = 10

for cross_op in crossover_ops:
  for mut_op in mutate_ops:
    print(left*generations)
    Individual.mutate    = mutate_ops[mut_op]
    Individual.crossover = crossover_ops[cross_op]
    
    start = time.time() #start time
    ga = GA(crossover_ops[cross_op], mutate_ops[mut_op], fitness_func, solution_generator, 1000, nw, elitism = 1, budget = BUDGET)
    
    avg_tour_length = []
    
    for data in ga.evolve(generations):
      avg_tour_length.append(data['Average Length of Tour'])
      
    end = time.time() #end time
    experiment['Fitness'].append(avg_tour_length)
    experiment['Cross'].append(cross_op)
    experiment['Mutate'].append(mut_op)
    performance['{0}, {1}'.format(cross_op, mut_op)] = 1.0/ga.best_found.get_fitness()
    budget_used['{0}, {1}'.format(cross_op, mut_op)] = ga.best_found.used_budget
    execution_time['{0}, {1}'.format(cross_op, mut_op)] = (end - start)
    solutions['{0}, {1}'.format(cross_op, mut_op)] = ga.best_found.genes
    
    left-=1
    
    
draw_convergence_figure(experiment['Fitness'], experiment['Cross'], experiment['Mutate'], performance, execution_time)
    
for s in solutions:
  print(s, 'tour length: ', performance[s])
  print('exec time:', execution_time[s])
  print('budget used', budget_used[s])
  visualize_with_path(nw, solutions[s], True)