import collections
import logging
import time

from argparse_dataclass import ArgumentParser

from algorithm import (Config, ImportData, InitialPopulation, Tree,
                       check_next_node, create_bpmn_model, create_test_tree,
                       utility)

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


def start(config_params: Config):
    start_time = time.time()
    log = ImportData(config_params.event_log_file)
    logging.info(log.trace_list)
    logging.info(log.unique_events)
    population = InitialPopulation(
        log.unique_events, config_params.initial_population_size
    )
    best_trees = utility.run(
        population.trees, log.unique_events, log.trace_list, config_params
    )
    for t in best_trees:
        logging.info(
            f"Tree: {t} Replay fitness: {t.replay_fitness} Precision: {t.precision} Simplicity: {t.simplicity} Generalization: {t.generalization} Fitness: {t.fitness}"
        )
    time_now = time.time()
    create_bpmn_model(t, time_now)
    with open(f"{time_now}-final_model.txt", 'w', encoding='utf-8') as f:
        f.write(f"Tree: {t}\nReplay fitness: {t.replay_fitness}\nPrecision: {t.precision}\nSimplicity: {t.simplicity}\nGeneralization: {t.generalization}\nFitness: {t.fitness}\n")
        for k, v in config_params.__dict__.items():
            f.write(f"{k}: {v}\n")
        f.write(f"Execution time: {time.time() - start_time}")
    logging.info(f"Execution time: {time.time() - start_time}")
    # logging.info(config_params.__dict__)


def test_loop(config):
    unique_events = {"A", "B", "C", "D"}
    traces = {
        "ABABAC": 1,
        "ABC": 1,
        "AC": 1,
        "DBABDC": 1,
        "ABADAC": 1,
        "AAC": 1,
        "ABAC": 1,
        "ABAD": 1,
        "BBBC": 1,
        "C": 1,
        "AAAA": 1,
        "ABAB": 1,
    }
    # traces = {"ABABAC": 1}
    # traces = {"AAAA": 1}
    # traces = { "AAC": 1}
    trees = utility.create_test_tree()
    for tree in trees:
        t = tree[0]
        res = tree[1]
        t.count_fitness(unique_events, traces, config)
        logging.info(
            f"Tree: {t} Replay fitness: {t.replay_fitness} match: {t.replay_fitness == res / len(traces)}"
        )


def test_prec():
    log = ImportData("event_logs/Artificial - Small Process.xes")
    log.extract_events()
    log.create_trace_list()
    log.trace_list.sort()
    traces_options = {}
    trace_frequency = {
        item: count for item, count in collections.Counter(log.trace_list).items()
    }
    # # get_beg = lambda count, trace: trace[:count]
    # for i in range(len(max(trace_frequency.keys(), key=len))):
    #     for trace in trace_frequency.keys():
    #         try:
    #             traces_options.setdefault(trace[:i], set()).add(trace[i])
    #         except IndexError:
    #             pass
    # traces_options2 = {}
    # for trace in trace_frequency.keys():
    #     for i in range(len(trace)):
    #         traces_options.setdefault(trace[:i], set()).add(trace[i])
    # print(traces_options)
    logging.info(trace_frequency.keys())
    logging.info(traces_options)
    # logging.info(traces_options2)
    logging.info(log.unique_events)
    tree = create_test_tree()
    logging.info(tree)

    # escaping_edges = {}
    # for partial_trace, options in traces_options.items():
    #     logging.info(partial_trace)
    #     # logging.info(partial_trace + "".join(list(log.unique_events)))
    #     possible_partial_trace = [partial_trace + activity for activity in list(log.unique_events) if activity not in traces_options[partial_trace]]
    #     logging.info(possible_partial_trace)
    #     for sub_trace in possible_partial_trace:
    #         _, match_len, *_ = check_next_node(tree[0], 0,sub_trace)
    #         logging.info(f"partial_trace {len(sub_trace)}  sub_trace {sub_trace}")
    #         if len(sub_trace) == match_len:
    #             escaping_edges.setdefault(partial_trace, set()).add(sub_trace[-1])
    #         logging.info(sub_trace)
    # logging.info(escaping_edges)
    # precision = 1 - (len(escaping_edges.values())/len(traces_options.values()))
    # logging.info(f"Precision {precision} !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    # _, i, _, _ = check_next_node(tree[0], 0, "abf")
    # logging.info(i)

#
# def test_tree_creation():
#     log = ImportData("event_logs/Artificial - Loan Process.xes")
#     log.extract_events()
#     log.create_trace_list()
#     # log.trace_list = [log.trace_list[-1]]
#     logging.info(log.trace_list)
#     logging.info(log.unique_events)
#     population = InitialPopulation(log.unique_events, 100)
#     population.create_initial_population()
#     trees = [create_tree(tree) for tree in population.trees]
#     # with open('trees.pkl', "wb") as pickle_file:
#     #     pickle.dump(trees, pickle_file)
#     # with open('to_check.pkl', "rb") as pickle_file:
#     #     trees = pickle.load(pickle_file)
#     # to_save = []
#     t = utility.create_test_tree()
#     utility.flattening_tree(t)
#     log.trace_list = list(set(log.trace_list))
#
#     logging.info(log.trace_list)
#     trace_frequency = {
#         item: count for item, count in collections.Counter(log.trace_list).items()
#     }
#     # char_frequency = {char: 0 for char in list(log.unique_events)}
#     # for trace, value in trace_frequency.items():
#     #     for item, count in collections.Counter(trace).items():
#     #         char_frequency[item] += count * value
#     # print(f"Char frequency: {char_frequency}")
#     t.count_fitness(log.unique_events, trace_frequency, 10, 5, 1, 0.1)
#     print(
#         f"Tree: {t} Replay fitness: {t.replay_fitness} Precision: {t.precision} Simplicity: {t.simplicity} Generalization: {t.generalization}Fitness: {t.fitness}"
#     )
#     # for tree in trees:
#     #     tree.count_fitness(log.unique_events, log.trace_list, 10, 5, 1, 0.1)
#     # logging.info(tree)
#     # if tree.replay_fitness > 0:
#     #     logging.info("Jest!!!!!!!!!!!!!!!!!!!")
#     # logging.info(f"Replay fitness: {tree.replay_fitness}")
#     # logging.info(f"Precision: {tree.precision}")
#     # logging.info(f"Simplicity: {tree.simplicity}")
#     # logging.info(f"Generalization: {tree.generalization}")
#     # logging.info(f"Fitness: {tree.fitness}")
#     #     if tree.replay_fitness >= 0.16:
#     #         to_save.append(tree)
#     # with open('to_check.pkl', "wb") as pickle_file:
#     #     pickle.dump(to_save, pickle_file)


if __name__ == "__main__":
    parser = ArgumentParser(Config)
    config = parser.parse_args()
    print(config.initial_population_size)
    # test_loop(config)

    start(config)

    # test_prec()
    # test()
    # test_tree_creation()
    # tree = create_test_tree()
    # print(tree)

    # run()
