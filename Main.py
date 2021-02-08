import collections
import logging
from argparse_dataclass import ArgumentParser

from algorithm import ImportData, InitialPopulation, Tree, create_tree, utility, create_bpmn_model, create_test_tree, Config

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    datefmt="%I:%M:%S",
    level=logging.INFO,
)

# dla olda to bylo
# SAMPLES = {
#     "→('a',+('b','c','d'),'f')": 4,
#     "→('a',X('b','c','d'),'e','f')": 1,
#     "X('e',+('a','b','c','d','f'))": 4,
#     "→('a',O('b','c','d','e'),'f')": 6,
#     "+('a',+('b','c','d'),'f')": 4,
#     "→('a','c',+('d','b'),'f')": 2,
#     "*('a',O('b','c',O('d','e')),f)": 6,
#     "O(→('a',+('c','b','d')),'e','f')": 4
# }

# def test():
#     log = ImportData("event_logs/Artificial - Small Process.xes")
#     log.extract_traces_and_events()
#     log.change_event_names()
#     logging.info(log.trace_list)
#     logging.info(log.unique_events)
#
#     population = InitialPopulation(log.unique_events, 8)
#     population.create_initial_population()
#     all_possible_traces = []
#     for n in range(1, len(log.unique_events) + 1):
#         all_possible_traces += ["".join(perm) for perm in permutations(log.unique_events, r=n)]
#     trees = []
#     for i in range(0, 8):
#         trees.append(Tree.Tree(population.trees[i]))
#         sample = [k for k, v in SAMPLES.items()][i]
#         trees[i].tree_model = sample
#         trees[i].count_fitness(10, 5, 1, log.trace_list, log.unique_events, all_possible_traces)
#         logging.info(
#             f"Tree: {trees[i].tree_model} Replay fitness: {trees[i].metrics['replay fitness']} Precision: {trees[i].metrics['precision']} Simplicity: {trees[i].metrics['simplicity']} Fitness: {trees[i].fitness} Regex: {trees[i].tree_regex}")
#         if trees[i].metrics['replay fitness'] != SAMPLES[sample]/6:
#             logging.info(f"Invalid regex match for {trees[i]}, expected {SAMPLES[sample]}, got {trees[i].metrics['replay fitness']}")


def start(config_params):
    log = ImportData("event_logs/Artificial - Loan Process.xes")
    log.extract_events()
    log.create_trace_list()
    logging.info(log.trace_list)
    logging.info(log.unique_events)
    population = InitialPopulation(log.unique_events, config_params.initial_population_size)
    population.create_initial_population()
    tree_list = []
    trace_frequency = {
        item: count for item, count in collections.Counter(log.trace_list).items()
    }
    # char_frequency = {char: 0 for char in list(log.unique_events)}
    # for trace, value in trace_frequency.items():
    #     for item, count in collections.Counter(trace).items():
    #         char_frequency[item] += count * value
    # print(f"Char frequency: {char_frequency}")
    for t in population.trees:
        tree = create_tree(t)
        tree.count_fitness(log.unique_events, trace_frequency, config_params)
        logging.info(
            f"Tree: {tree} Replay fitness: {tree.replay_fitness} Precision: {tree.precision} Simplicity: {tree.simplicity} Generalization: {tree.generalization} Fitness: {tree.fitness}"
        )
        tree_list.append(tree)
    logging.info("Przed run")
    best_trees = utility.run(tree_list, log.unique_events, log.trace_list, config_params)
    logging.info("Przed run")
    for t in best_trees:
        print(
            f"Tree: {t} Replay fitness: {t.replay_fitness} Precision: {t.precision} Simplicity: {t.simplicity} Generalization: {t.generalization} Fitness: {t.fitness}"
        )


def test_tree_creation():
    log = ImportData("event_logs/Artificial - Loan Process.xes")
    log.extract_events()
    log.create_trace_list()
    # log.trace_list = [log.trace_list[-1]]
    logging.info(log.trace_list)
    logging.info(log.unique_events)
    population = InitialPopulation(log.unique_events, 100)
    population.create_initial_population()
    trees = [create_tree(tree) for tree in population.trees]
    # with open('trees.pkl', "wb") as pickle_file:
    #     pickle.dump(trees, pickle_file)
    # with open('to_check.pkl', "rb") as pickle_file:
    #     trees = pickle.load(pickle_file)
    # to_save = []
    t = utility.create_test_tree()
    utility.flattening_tree(t)
    log.trace_list = list(set(log.trace_list))
    logging.info(log.trace_list)
    trace_frequency = {
        item: count for item, count in collections.Counter(log.trace_list).items()
    }
    # char_frequency = {char: 0 for char in list(log.unique_events)}
    # for trace, value in trace_frequency.items():
    #     for item, count in collections.Counter(trace).items():
    #         char_frequency[item] += count * value
    # print(f"Char frequency: {char_frequency}")
    t.count_fitness(log.unique_events, trace_frequency, 10, 5, 1, 0.1)
    print(
        f"Tree: {t} Replay fitness: {t.replay_fitness} Precision: {t.precision} Simplicity: {t.simplicity} Generalization: {t.generalization}Fitness: {t.fitness}"
    )
    # for tree in trees:
    #     tree.count_fitness(log.unique_events, log.trace_list, 10, 5, 1, 0.1)
    # logging.info(tree)
    # if tree.replay_fitness > 0:
    #     logging.info("Jest!!!!!!!!!!!!!!!!!!!")
    # logging.info(f"Replay fitness: {tree.replay_fitness}")
    # logging.info(f"Precision: {tree.precision}")
    # logging.info(f"Simplicity: {tree.simplicity}")
    # logging.info(f"Generalization: {tree.generalization}")
    # logging.info(f"Fitness: {tree.fitness}")
    #     if tree.replay_fitness >= 0.16:
    #         to_save.append(tree)
    # with open('to_check.pkl', "wb") as pickle_file:
    #     pickle.dump(to_save, pickle_file)


if __name__ == "__main__":
    parser = ArgumentParser(Config)
    config = parser.parse_args()
    print(config.initial_population_size)
    start(config)
    # test()
    # test_tree_creation()
    # tree = create_test_tree()
    # print(tree)
    # create_bpmn_model(tree)
    # run()
