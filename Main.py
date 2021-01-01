import logging
from itertools import chain, permutations

import utility
import Tree
from Data import ImportData
from InitialPopulation import InitialPopulation
import datetime

logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s %(message)s', datefmt='%I:%M:%S', level=logging.INFO)

def test():
    log = ImportData("Artificial - Small Process.xes")
    log.extract_traces_and_events()
    logging.info(log.trace_list)
    logging.info(log.unique_events)
    samples = {
        "→('a',+('b','c','d'),'f')": 4,
        "→('a',X('b','c','d'),'e','f')": 1,
        "X('e',+('a','b','c','d','f'))": 4,
        "→('a',O('b','c','d','e'),'f')": 6,
        "+('a',+('b','c','d'),'f')": 4,
        "→('a','c',+('d','b'),'f')": 2,
        "*('a',O('b','c',O('d','e')),f)": 6,
        "O(→('a',+('c','b','d')),'e','f')": 4
    }
    population = InitialPopulation(log.unique_events, 8)
    population.create_initial_population()
    all_possible_traces = []
    for n in range(1, len(log.unique_events) + 1):
        all_possible_traces += ["".join(perm) for perm in permutations(log.unique_events, r=n)]
    trees = []
    for i in range(0, 8):
        trees.append(Tree.Tree(population.trees[i]))
        sample = [k for k, v in samples.items()][i]
        trees[i].tree_model = sample
        trees[i].count_fitness(10, 5, 1, log.trace_list, log.unique_events, all_possible_traces)
        logging.info(
            f"Tree: {trees[i].tree_model} Replay fitness: {trees[i].metrics['replay fitness']} Precision: {trees[i].metrics['precision']} Simplicity: {trees[i].metrics['simplicity']} Fitness: {trees[i].fitness} Regex: {trees[i].tree_regex}")
        if trees[i].metrics['replay fitness'] != samples[sample]/6:
            logging.info(f"Invalid regex match for {trees[i]}, expected {samples[sample]}, got {trees[i].metrics['replay fitness']}")

def start():
    log = ImportData("Artificial - Small Process.xes")
    log.extract_traces_and_events()
    logging.info(log.trace_list)
    logging.info(log.unique_events)
    population = InitialPopulation(log.unique_events, 100)
    population.create_initial_population()
    all_possible_traces = []
    for n in range(1, len(log.unique_events) + 1):
        all_possible_traces += ["".join(perm) for perm in permutations(log.unique_events, r=n)]
    # all_possible_traces = ["".join(perm) for perm in permutations(log.unique_events)]
    # print(all_possible_traces)
    # print(len(all_possible_traces))
    tree_list = []
    for t in population.trees:
        tree = Tree.Tree(t)
        # tree.tree_model = "+('a','b','c')"
        # tree.tree_model = "+(O('a','b'),'c')"
        # tree.tree_model = "*(*('a','d','c'),'g','f')"

        # tree.count_fitness(10, 5, 1, log.trace_list, log.unique_events, all_possible_traces)
        tree_list.append(tree)
    utility.flattening_tree(tree_list)
    for tree in tree_list:
        tree.count_fitness(10, 5, 1, log.trace_list, log.unique_events, all_possible_traces)
        logging.info(tree.tree_regex)

        # print(str(tree))
        # reg = utility.create_tree_regex(str(tree))
        # matches, quality_map[str(tree)] = utility.count_replay_fitness(reg, log.trace_list)
        # precision = utility.count_precision(all_possible_traces, reg, matches)
        # print(f"Precision: {precision}")
        # print(utility.count_simplicity(str(tree), log.unique_events))
    # To zakomentowalem
    best_trees = utility.run(tree_list, log.unique_events, log.trace_list, all_possible_traces, 400, 0.8)
    for t in best_trees:
        print(
            f"Tree: {t.tree_model} Replay fitness: {t.metrics['replay fitness']} Precision: {t.metrics['precision']} Simplicity: {t.metrics['simplicity']} Fitness: {t.fitness} Regex: {t.tree_regex}")

    # logging.info([i.fitness for i in worst_list])

    # for t in worst_list_after_change:
    #     t.count_fitness(10, 5, 1, log.trace_list, log.unique_events, all_possible_traces)
    # logging.info([i.fitness for i in worst_list_after_change])
    #
    #
    #
    # logging.info([i.fitness for i in worst_list_after_change])
    # logging.info("Max: " + str(max([i.fitness for i in worst_list_after_change])))
    # print({k: v for k, v in sorted(quality_map.items(), reverse=True, key=lambda item: item[1])})

    # print(log.event_log[0])
    # print(log.event_log[0][0]['concept:name'])


if __name__ == "__main__":
 # start()
 test()

