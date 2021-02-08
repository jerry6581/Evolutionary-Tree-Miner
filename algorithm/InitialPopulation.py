import logging

from pm4py.simulation.tree_generator import simulator as tree_gen
from pm4py.simulation.tree_generator.variants.ptandloggenerator import GeneratedTree


class InitialPopulation:
    def __init__(self, unique_events, population_size):
        self.logger = logging.getLogger(__name__)
        self.unique_events = list(unique_events)
        self.population_size = population_size
        self.trees = []
        GeneratedTree.alphabet = list(unique_events)

    def create_initial_population(self):
        parameters = {
            "min": len(self.unique_events),
            "max": 2 * len(self.unique_events),
            "mode": 3 * len(self.unique_events) / 2,
            "silent": 0,
        }
        for i in range(self.population_size):
            self.trees.append(tree_gen.apply(parameters=parameters))
