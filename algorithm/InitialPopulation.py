from pm4py.simulation.tree_generator import simulator as tree_gen
from pm4py.simulation.tree_generator.variants.ptandloggenerator import \
    GeneratedTree

from .Tree import Tree


class InitialPopulation:
    def __init__(self, unique_events, population_size):
        self.unique_events = list(unique_events)
        self.population_size = population_size
        self.trees = []
        self.create_initial_population()

    def create_initial_population(self):
        GeneratedTree.alphabet = list(self.unique_events)
        parameters = {
            "min": len(self.unique_events),
            "max": 2 * len(self.unique_events),
            "mode": 3 * len(self.unique_events) / 2,
            "silent": 0,
            "loop": 0.1,
            "or": 0.2,
            "parallel": 0.2,
            "choice": 0.2,
            "sequence": 0.3,
        }
        for i in range(self.population_size):
            tree = create_tree(tree_gen.apply(parameters=parameters))
            self.trees.append(tree)


def create_tree(process_tree, parent=None):
    label = process_tree.label if process_tree.label else process_tree.operator.value
    tree = Tree(label.replace("->", "→").replace("O", "v").replace("+", "∧"), parent, None)
    children = [
        create_tree(child_process_tree, tree)
        for child_process_tree in process_tree.children
    ]
    tree.children = children
    return tree
