#    This file is part of DEAP.
#
#    DEAP is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by the Free Software Foundation, either version 3 of
#    the License, or (at your option) any later version.
#
#    DEAP is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public
#    License along with DEAP. If not, see <http://www.gnu.org/licenses/>.


#    example which maximizes the sum of a list of integers
#    each of which can be 0 or 1

import random
import numpy as np

from deap import base
from deap import creator
from deap import tools
import pickle
import copy
import sys
import numpy 
import time
NGEN = 1000
pop_size = 4 * 75
cxpb = .8
m_fac = .2
m_prob = .2


np.random.seed(10)
rng = np.random
pstri = "./pickle_jar/"


fs = open(pstri + "tar_data_with_dic.pickle", "rb")
tup_t = pickle.load(fs)
fs.close()
target_arr, target_label,  target_dic = tup_t

dum_arr = target_label.reshape((target_label.shape[0], 1))
clumped_arr = np.concatenate((target_arr, dum_arr), axis=1)

# print(dic)
numlis = np.arange(clumped_arr.shape[0])
rng.shuffle(numlis)
clumped_arr = clumped_arr[numlis]
# clumped_arr = clumped_arr[ numlis ]
clumped_target = clumped_arr[:]
ann = int((3/4)*clumped_target.shape[0])
print(ann)
tup_t = (target_rest_arr, target_rest_label), (target_test_arr, target_test_label) = (clumped_target[:ann, :-1], clumped_target[:ann, -1:]), (clumped_target[ann:, :-1], clumped_target[ann:, -1:])
#print(tup_t)
fs = open(pstri + "tar_tup.pickle", "wb")
pickle.dump(tup_t, fs)
fs.close()

target_dim = target_rest_arr.shape[1]


fs = open(pstri + "src_data_with_dic.pickle", "rb")
tup_s = pickle.load(fs)
fs.close()
source_arr, source_label, source_dic = tup_s


dum_arr = source_label.reshape((source_label.shape[0], 1))
clumped_arr = np.concatenate((source_arr, dum_arr), axis=1)
# print(dic)
numlis = np.arange(clumped_arr.shape[0])
rng.shuffle(numlis)
clumped_arr = clumped_arr[numlis]
# clumped_arr = clumped_arr[ numlis ]
clumped_source = clumped_arr[:]
#ann = (3//4)*clumped_source.shape[0]
ann  = clumped_source.shape[0]
tup_s = (source_rest_arr, source_rest_label), (source_test_arr, source_test_label) = (clumped_source[:ann, :-1], clumped_source[:ann, -1:]), (clumped_source[ann:, :-1], clumped_source[ann:, -1:])
fs = open(pstri + "src_tup.pickle", "wb")
pickle.dump(tup_s, fs)
fs.close()
source_dim = source_rest_arr.shape[1]

creator.create("FitnessMin", base.Fitness, weights=(-1.0, -1.0))
class MatChromo:
	def __init__(self, source_dim, target_dim, arr=None, rng = np.random):
		self.array = rng.random((source_dim, target_dim))
creator.create("Individual", MatChromo, fitness=creator.FitnessMin)


toolbox = base.Toolbox()

# Attribute generator
#                      define 'attr_bool' to be an attribute ('gene')
#                      which corresponds to integers sampled uniformly
#                      from the range [0,1] (i.e. 0 or 1 with equal
#                      probability)
#toolbox.register("attr_bool", random.randint, 0, 1)
def return_obj(class_name, source_dim, target_dim):
	return class_name(source_dim, target_dim)
# Structure initializers
#                         define 'individual' to be an individual
#                         consisting of 100 'attr_bool' elements ('genes')
toolbox.register("individual", return_obj, creator.Individual,source_dim, target_dim )

# define the population to be a list of individuals
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

# the goal ('fitness') function to be maximized

def dist(transformed_target, source_instance):
	return np.sqrt(np.sum((transformed_target - source_instance)**2))


def closeness_cost(ind):
	sumi = 0
	W = ind.array
	#W = np.identity(W.shape[0])
	# print( source_dic)

	#print(target_rest_label)
	for target_instance, target_lab in zip(target_rest_arr, target_rest_label):
		# assert (target_instance in source_rest_arr)
		
		min_dist = np.inf
		target_instance = np.reshape(target_instance, (target_instance.shape[0], 1))
		

		transformed_target = np.dot(W, target_instance)
		transformed_target = np.ravel(transformed_target)

		#assert (transformed_target in source_rest_arr)
		#print(source_rest_arr.shape)
		for source_instance, source_lab in zip(source_rest_arr, source_rest_label):
			#print("here")
			# print(transformed_target, source_instance)
			#print(source_instance)
			if source_lab == target_lab:
				min_dist = min(min_dist, dist(transformed_target, source_instance))
			#print(min_dist)
		sumi += min_dist

	# sumi += np.sum(abs(W - np.identity(W.shape[0], 'float32')))
	# print( sumi )
	return (sumi, np.sum(abs(W - np.identity(W.shape[0], 'float32'))))

#----------
# Operator registration
#----------imp
# register the goal / fitness function
toolbox.register("evaluate", closeness_cost)

# register the crossover operator
def myCrossover(darr1, darr2, cxpb, rng = np.random):
	arr1 = darr1.array
	arr2 = darr2.array
	for row in range(arr1.shape[0]):
		for col in range(arr1.shape[1]):
			if rng.random() < cxpb:
				alpha = rng.random()
				temp = copy.deepcopy(arr1[row][col])
				arr1[row][col] = alpha*arr1[row][col] + (1-alpha)*arr2[row][col]
				arr2[row][col] = alpha*arr2[row][col] + (1-alpha)*temp
	del darr1.fitness.values
	del darr2.fitness.values
	return darr1, darr2
toolbox.register("mate", myCrossover, rng = np.random)

# register a mutation operator with a probability to
# flip each attribute/gene of 0.05

def myMutate(darr, m_prob, m_fac = 1, rng = np.random):
	arr = darr.array
	for row in range(arr.shape[0]):
		index = rng.randint(0, arr.shape[1])
		if rng.random() < m_prob:
			arr[row][index] += rng.uniform(-1, 1)*m_fac
	del(darr.fitness.values)

toolbox.register("mutate", myMutate, rng = np.random)

# operator for selecting individuals for breeding the next
# generation: each individual of the current generation
# is replaced by the 'fittest' (best) of three individuals
# drawn randomly from the current generation.
toolbox.register("select", tools.selNSGA2)
#toolbox.register("select", tools.selRoulette)
#----------
def ensemble(pop_lis):
	new_3d_arr = np.array([item.array for item in pop_lis])
	me = np.mean(new_3d_arr, axis = 0)
	assert ( me.shape == pop_lis[0].array.shape)
	return me


def main():
	random.seed(1064)
	global NGEN, pop_size
	# create an initial population of 300 individuals (where
	# each individual is a list of integers)
	pop = toolbox.population(n=pop_size)

	# CXPB  is the probability with which two individuals
	#       are crossed
	#
	# MUTPB is the probability for mutating an individual
	CXPB, MUTPB = 0.5, 0.2
	
	stats = tools.Statistics(lambda ind: ind.fitness.values)
	# stats.register("avg", numpy.mean, axis=0)
	# stats.register("std", numpy.std, axis=0)
	stats.register("min", numpy.min, axis=0)
	stats.register("max", numpy.max, axis=0)
	
	logbook = tools.Logbook()
	logbook.header = "gen", "evals", "std", "min", "avg", "max"
	#print("Start of evolution")

	# Evaluate the entire population
	fitnesses = list(map(toolbox.evaluate, pop))
	#print(fitnesses)
	for ind, fit in zip(pop, fitnesses):
		ind.fitness.values = fit

	#print("  Evaluated %i individuals" % len(pop))

	# Extracting all the fitnesses of
	fits = [ind.fitness.values[0] for ind in pop]
	pop = toolbox.select(pop, len(pop))
	# Variable keeping track of the number of generations
	g = 0

	# Begin the evolution
	while g < NGEN:
		# A new generation
		g = g + 1
		#print("-- Generation %i --" % g)
		offspring = tools.selTournamentDCD(pop, len(pop))
		offspring = [toolbox.clone(ind) for ind in offspring]
		# Select the next generation individuals
		#offspring = toolbox.select(pop, len(pop))
		# Clone the selected individuals
		#offspring = list(map(toolbox.clone, offspring))

		# Apply crossover and mutation on the offspring
		for child1, child2 in zip(offspring[::2], offspring[1::2]):


			toolbox.mate(child1, child2, CXPB)



		for mutant in offspring:

			# mutate an individual with probability MUTPB

			toolbox.mutate(mutant, MUTPB)
			#del mutant.fitness.values
		

		# Evaluate the individuals with an invalid fitness
		invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
		fitnesses = map(toolbox.evaluate, invalid_ind)
		for ind, fit in zip(invalid_ind, fitnesses):
			ind.fitness.values = fit

		

		
		fits = [ind.fitness.values[0] for ind in pop]


	   
		pop = toolbox.select(pop + offspring, pop_size)
		record = stats.compile(pop)
		logbook.record(gen=g, evals=len(invalid_ind), **record)
	print(logbook.stream)
	#ind_min = np.argmin(fitnesses)
	decided_ar = ensemble(pop)

	#print(decided_ar)
	post_st = sys.argv[1]
	fs= open("./pickle_jar/dublue_t_ensemble"+post_st+".pickle", "wb")
	pickle.dump(decided_ar, fs)
	print(decided_ar)
	fs.close()
	print("-- End of (successful) evolution --")

	best_ind = tools.selBest(pop, 1)[0]
	print("Best individual is %s, %s" % (best_ind.array, best_ind.fitness.values))

if __name__ == "__main__":
	main()
