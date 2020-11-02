import treelib
import pandas as pd
import pm4py
import random
import re
from itertools import permutations

event_list = ("a", "bb", "cc", "dd", "ee", "ff", "gg", "hh")
operator_map = {
    "parallel execution": {"value": u"\u02C4", "nodes": 2},
    "non-exclusive choice": {"value": u"\u02C5", "nodes": 2},
    "exclusive choice": {"value": "x", "nodes": 2},
    "sequential execution": {"value": u"\u2192", "nodes": len(event_list)},
    "repeated execution": {"value": u"\u21BA", "nodes": 3},
}
# class ImportData:
#
#     def __init__(self, path):
#         self.event_log = pm4py.read_xes(path)
#         # self.input_data = pd.read_csv(path)
#
#
# log = ImportData("Artificial - Small Process.xes")
# print(log.event_log[0][0])
# case = import_data.input_data.loc[import_data.input_data["Case ID"] == 1]
# print(case["Activity"])
# case = import_data.input_data.loc[import_data.input_data["Case ID"] == 2]
# print(case["Activity"])
# case = import_data.input_data.loc[import_data.input_data["Case ID"] == 3]
# print(case["Activity"])
# print(import_data.input_data["Case ID"] == 1)

# pm4py supports access and manipulation of event log data through the IEEE XES- and csv format.

# print(operator_map)
random.seed(6)


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
# GeneratedTree.alphabet = event_list
parameters = {"min": 8, "max": 10, "mode": 9}

from pm4py.evaluation.replay_fitness import evaluator as replay_fitness_evaluator

def create_regex(tree_model: str) -> str:
    tree_model = tree_model.replace(" ", "")
    # regex_parallel = r"\+\(('(\w)'[,]?|(τ)[,]?)*\)"
    regex_parallel = r"(\+\(('\w'[,]?|τ[,]?)*\))"
    pattern = re.compile(regex_parallel)
    res = pattern.findall(tree_model)
    print(res)
    print(tree_model)
    if res:
        for group in res:
            g = group[0]
            print(g)
            proc = re.findall(r"[\wτ]", g)
            print(proc)
            perm = permutations(proc)
            reg = "(" + "|".join(["".join(per) for per in list(perm)]) + ")"  # TODO zmien jak beda normalne dane
            print(reg)
            tree_model = tree_model.replace(g, reg)
    return tree_model
    # print(tree_model)
    # print(pattern.findall(tree_model))
    # print(pattern.search(tree_model).group(0))
    # n = 0
    # stack = []
    # sign = tree_model[n]
    # if sign == "-":
    #     stack.append("(")
    #     n += 4
    #
    # elif sign == "+":
    #     stack.append("(")
    #     n += 3
    # elif sign == "X":
    #
    # elif sign == "*":

    # elif sign == "O":

for i in range(10):
    tree = tree_gen.apply(parameters=parameters)
# for _tree in tree:
    print(create_regex(str(tree) + str(tree).replace("a", "h").replace("g", "i")))
    print()