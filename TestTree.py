import collections
from typing import List, Any
from pm4py.objects.process_tree.process_tree import ProcessTree
import logging
import math


class Tree:
    def __init__(self, label: str, parent: "Tree", children: List["Tree"] = None):
        self.parent = parent
        self.label = label
        self.children = children if children else []
        self.replay_fitness = None
        self.simplicity = None
        self.precision = None
        self.generalization = None
        self.fitness = None

    def __repr__(self):
        return str(self)

    def __str__(self):
        if self.children:
            children = ",".join([str(child) for child in self.children])
            return f"{self.label}({children})"
        else:
            return self.label

    def __gt__(self, other):
        return self.fitness > other.fitness

    # def __eq__(self, other):
    #     return self.label == other.label
    #
    # def __hash__(self):
    #     to_hash = [child for child in self.children]
    #     to_hash.append(self.label)
    #     return hash(tuple(to_hash))

    def count_simplicity(self, unique_events):
        all_leaves = []
        find_nodes(self, all_leaves)
        all_leaves = [t for t in all_leaves if str(t) != 'τ']
        leaves = [str(t) for t in all_leaves]
        # leaves = list(filter('τ'.__ne__, leaves))
        # print(f"Leaves: {leaves}")
        denominator = len(leaves) + len(list(unique_events))
        unique_events_in_tree = set(leaves)
        # print(f"Unique events in tree: {unique_events_in_tree}")
        missing_events = len(list(unique_events)) - len(list(unique_events_in_tree))
        # print(f"Missing: {missing_events}")
        duplicated_activities = sum([count - 1 for item, count in collections.Counter(leaves).items() if
                                 count > 1])
        # print(f"Duplicated: {duplicated_activities}")
        counter = missing_events + duplicated_activities
        self.simplicity = 1 - counter/denominator
        # print(f"Simplicity: {self.simplicity}")
        return all_leaves

    def count_replay_fitness_and_precision(self, trace_list, all_leaves):
        denominator = len(trace_list)
        counter = 0
        matches = 0
        executions = {str(tree): 0 for tree in all_leaves}
        for trace in trace_list:
            if_match, visited_nodes, executions_list = compare_to_trace(self, trace)
            if if_match:
                matches += 1
                counter += (len(executions_list) * (len(all_leaves) - len(list(visited_nodes))) / len(all_leaves))
                for item, count in collections.Counter([str(t) for t in executions_list]).items():
                    executions[item] += count
        self.replay_fitness = matches / len(trace_list)
        self.precision = (1 - (counter / denominator)) if counter > 0 else 0
        generalization_counter = 0
        for key in executions.keys():
            generalization_counter += pow(math.sqrt(executions[key]), -1) if executions[key] > 0 else 0
        self.generalization = (1 - (generalization_counter/len(all_leaves))) if generalization_counter > 0 else 0

    def count_fitness(self, unique_events, trace_list, replay_fitness_w, precision_w, simplicity_w, generalization_w):
        all_leaves = self.count_simplicity(unique_events)
        self.count_replay_fitness_and_precision(trace_list, all_leaves)
        self.fitness = (replay_fitness_w * self.replay_fitness + simplicity_w * self.simplicity + precision_w * self.precision + generalization_w * self.generalization) / (replay_fitness_w + precision_w + simplicity_w + generalization_w)


def create_tree(process_tree: ProcessTree, parent=None):
    label = process_tree.label if process_tree.label else process_tree.operator.value
    tree = Tree(label, parent, None)
    children = [create_tree(child_process_tree, tree) for child_process_tree in process_tree.children]
    tree.children = children
    return tree


def find_nodes(tree: Tree, tree_list):
    if not tree.children:
        tree_list.append(tree)
    for child_tree in tree.children:
        find_nodes(child_tree, tree_list)


def find_operator_nodes(tree: Tree, operator_list):
    if tree.children:
        operator_list.append(tree)
    for child_tree in tree.children:
        find_operator_nodes(child_tree, operator_list)


def find_next_node(start_tree, i, trace):
    visited_nodes = list()
    error = False
    if start_tree.label == "+":
        children = list(start_tree.children)
        for _ in range(len(children)):
            for child in children:
                if child.children:
                    _i = i
                    start_tree, i, error, visited_child_nodes = find_next_node(child, i, trace)
                    if not error:
                        children.remove(child)
                        visited_nodes += visited_child_nodes
                    else:
                        i = _i
                try:
                    if child.label == trace[i]:
                        children.remove(child)
                        i += 1
                        visited_nodes.append(child)
                except IndexError:
                    logging.debug("Trace is too short to validate against this tree.")
                if child.label == "τ":
                    children.remove(child)
            if not children: break
        if children: error = True
    elif start_tree.label == "→":
        for child in start_tree.children:
            if child.children:
                start_tree, i, error, visited_child_nodes = find_next_node(child, i, trace)
                if not error:
                    visited_nodes += visited_child_nodes
                    continue
                else:
                    error = True
                    break

            if len(trace) > i and child.label == trace[i]:
                i += 1
                visited_nodes.append(child)
            elif child.label == "τ":
                pass
            else:
                error = True
                break
    elif start_tree.label == "O":
        children = list(start_tree.children)
        start_len = len(children)
        for _ in range(len(children)):
            for child in children:
                if child.children:
                    _i = i
                    start_tree, i, error, visited_child_nodes = find_next_node(child, i, trace)
                    if not error:
                        children.remove(child)
                        visited_nodes += visited_child_nodes
                    else:
                        i = _i  # bo jak find_next_node zwroci blad to sie chcemy sie przesuwac w trace wiec wracamy
                try:
                    if child.label == trace[i]:
                        children.remove(child)
                        i += 1
                        visited_nodes.append(child)
                except IndexError:
                    pass
            if not children: break
        if start_len == len(children):
            error = True
    elif start_tree.label == "X":
        children = list(start_tree.children)
        start_len = len(children)
        for _ in range(len(children)):
            for child in children:
                if child.children:
                    _i = i
                    start_tree, i, error, visited_child_nodes = find_next_node(child, i, trace)
                    if not error:
                        children.remove(child)
                        visited_nodes += visited_child_nodes
                    else:
                        i = _i
                try:
                    if child.label == trace[i]:
                        children.remove(child)
                        i += 1
                        visited_nodes.append(child)
                except IndexError:
                    pass
            if not children: break
        if start_len != len(children) + 1:
            error = True
    elif start_tree.label == "*":
        do = start_tree.children[0]
        redo = start_tree.children[1]
        exit_loop = start_tree.children[2]
        if len(trace) > i and do.label == trace[i]:
            i += 1
            visited_nodes.append(do)
            if len(trace) > i and redo.label == trace[i]:
                i += 1
                visited_nodes.append(redo)
                start_tree, i, error, visited_child_nodes = find_next_node(start_tree, i, trace)
                if not error:
                    visited_nodes += visited_child_nodes
            elif redo.children and not find_next_node(redo, i, trace)[2]:
                save_tree = start_tree
                start_tree, i, error, visited_child_nodes = find_next_node(redo, i, trace)
                if not error:
                    visited_nodes += visited_child_nodes
                    start_tree, i, error, visited_child_nodes = find_next_node(save_tree, i, trace)
                    if not error:
                        visited_nodes += visited_child_nodes
            elif len(trace) > i and exit_loop.label == trace[i]:
                i += 1
                visited_nodes.append(exit_loop)
            elif exit_loop.children:
                _i = i
                start_tree, i, error, visited_child_nodes = find_next_node(exit_loop, i, trace)
                if error:
                    i = _i
                else:
                    visited_nodes += visited_child_nodes
            else:
                error = True
        elif do.children:
            save_tree = start_tree
            start_tree, i, error, visited_child_nodes = find_next_node(do, i, trace)
            if not error:
                visited_nodes += visited_child_nodes
                if len(trace) > i and redo.label == trace[i]:
                    i += 1
                    visited_nodes.append(redo)
                    start_tree, i, error, visited_child_nodes = find_next_node(save_tree, i, trace)
                    if not error:
                        visited_nodes += visited_child_nodes
                elif redo.children and not find_next_node(redo, i, trace)[2]:
                    save_tree = save_tree
                    start_tree, i, error, visited_child_nodes = find_next_node(redo, i, trace)
                    if not error:
                        visited_nodes += visited_child_nodes
                        start_tree, i, error, visited_child_nodes = find_next_node(save_tree, i, trace)
                        if not error:
                            visited_nodes += visited_child_nodes
                elif len(trace) > i and exit_loop.label == trace[i]:
                    i += 1
                    visited_nodes.append(exit_loop)
                elif exit_loop.children:
                    _i = i
                    start_tree, i, error, visited_child_nodes = find_next_node(exit_loop, i, trace)
                    if error:
                        i = _i
                    else:
                        visited_nodes += visited_child_nodes
                else:
                    error = True
        else:
            error = True

    return start_tree, i, error, visited_nodes


def compare_to_trace(start_tree: Tree, trace: str):
    start_tree, i, error, visited_nodes = find_next_node(start_tree, 0, trace)
    if i != len(trace):
        error = True
    visited_nodes = visited_nodes if not error else set()
    visited_nodes_set = set(visited_nodes)
    if not error:
        logging.info(visited_nodes_set)
    return not error, visited_nodes_set, visited_nodes


#     if tree.label == "O":
#         for child in tree.children:
#
#         possible_char =
logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s %(message)s', datefmt='%I:%M:%S', level=logging.INFO)

sample_tree = Tree("X", None)
sample_tree.children.append(Tree("c", sample_tree))
sample_tree.children.append(Tree("f", sample_tree))
sample_tree.children.append(Tree("a", sample_tree))
sample_tree.children.append(Tree("d", sample_tree))
sample_tree.children.append(Tree("e", sample_tree))
sample_tree.children.append(Tree("b", sample_tree))

# sample_sub_tree_2 = Tree("*", sample_tree)
# sample_tree.children.append(sample_sub_tree)
# sample_tree.children.append(sample_sub_tree_2)
# sample_sub_tree_2.children.append(Tree("b", sample_sub_tree_2))
# sample_sub_sub_tree = Tree("X", sample_sub_tree_2)
# sample_sub_tree_2.children.append(sample_sub_sub_tree)
# sample_sub_sub_tree.children.append(Tree("c", sample_sub_sub_tree))
# sample_sub_sub_tree.children.append(Tree("d", sample_sub_sub_tree))
# sample_sub_tree_2.children.append(Tree("e", sample_sub_tree_2))

print(sample_tree)

# print(find_node(sample_tree, "d"))
t = str(sample_tree)
print("abcbdbe")
print(compare_to_trace(sample_tree, "abcbcbe"))
sample_tree.count_fitness(["a", "b", "c", "d", "e", "f"],  ['abdcf', 'acbdf', 'acdbf', 'adef', 'abcdf', 'aedf'], 1,1,1,1)
print(f"Replay fitness {sample_tree.replay_fitness}")
unique_events = {"a", "b", "c", "d", "e"}
sample_tree.count_simplicity(unique_events)
# tree_list = []
# find_nodes(sample_tree, tree_list)
# print(tree_list)