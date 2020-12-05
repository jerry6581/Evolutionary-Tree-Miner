import logging
from itertools import chain, permutations

import utility
import Tree
from Data import ImportData
from InitialPopulation import InitialPopulation

logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s %(message)s', datefmt='%I:%M:%S', level=logging.INFO)

if __name__ == "__main__":

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
        tree = Tree.Tree(str(t))
        tree.count_fitness(10, 5, 1, log.trace_list, log.unique_events, all_possible_traces)
        tree_list.append(tree)
        # print(str(tree))
        # reg = utility.create_tree_regex(str(tree))
        # matches, quality_map[str(tree)] = utility.count_replay_fitness(reg, log.trace_list)
        # precision = utility.count_precision(all_possible_traces, reg, matches)
        # print(f"Precision: {precision}")
        # print(utility.count_simplicity(str(tree), log.unique_events))
    best_trees = utility.run(tree_list, log.unique_events, log.trace_list, all_possible_traces, 100, 0.8)
    for t in best_trees:
        print(f"Tree: {t.tree_model} Replay fitness: {t.metrics['replay fitness']} Precision: {t.metrics['precision']} Simplicity: {t.metrics['simplicity']} Fitness: {t.fitness}")

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