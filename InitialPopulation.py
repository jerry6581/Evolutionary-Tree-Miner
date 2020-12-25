import treelib
import pandas as pd
import pm4py
import random
import basic_tree
import logging
from pm4py.simulation.tree_generator.variants.ptandloggenerator import GeneratedTree

random.seed(7)

class InitialPopulation:

    def __init__(self, unique_events, population_size):
        self.logger = logging.getLogger(__name__)
        self.unique_events = list(unique_events)
        self.population_size = population_size
        self.trees = []
        GeneratedTree.alphabet = list(unique_events)

    def create_initial_population(self):
        # parameters = {"events": self.unique_events}
        parameters = {"min": len(self.unique_events), "max": 2*len(self.unique_events), "mode": 3*len(self.unique_events)/2, "silent": 0}
        for i in range(self.population_size):
            self.trees.append(tree_gen.apply(parameters=parameters))
            # self.logger.info(self.trees[i])




# def generate_random_tree():
#     event_list_to_modify = list(event_list)
#     tree = treelib.Tree()
#     tree.create_node(
#         operator_map["sequential execution"], "sequential execution"
#     )  # root node
#     parent = "sequential execution"
#     i = 0
#     while event_list_to_modify:
#         if random.randint(0, 1) == 0:
#             node = random.choice(event_list_to_modify)
#             tree.create_node(node, node, parent=parent)
#             event_list_to_modify.remove(node)
#         else:
#             i += 1
#             node = random.choice(list(operator_map.values()))["value"]
#             tree.create_node(node, f"node-{i}", parent=parent)
#             parent = f"node-{i}"
#     print(tree)


# generate_random_tree()
from pm4py.simulation.tree_generator import simulator as tree_gen
from pm4py.simulation.tree_generator.variants.ptandloggenerator import GeneratedTree
# from pm4py.simulation.tree_generator.variants.basic

# GeneratedTree.alphabet = ['a', 'b', 'c', 'd', 'e', 'f' ]
parameters = {"min": 9, "max": 10, "mode": 9}

from pm4py.evaluation.replay_fitness import evaluator as replay_fitness_evaluator


