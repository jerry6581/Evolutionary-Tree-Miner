import collections
import logging
import math
from typing import Any, List

from pm4py.objects.process_tree.process_tree import ProcessTree

from . import Config


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

    # dodac moze jeszcze useless nodes? TODO i liczyc tau jako useless - czyli bez usuwania tau z all_leaves oraz petle gdzie sa tały
    def count_simplicity(self, unique_events):
        all_leaves = []
        find_nodes(self, all_leaves)
        all_leaves = [t for t in all_leaves if str(t) != "τ"]
        leaves = [str(t) for t in all_leaves]
        denominator = len(leaves) + len(list(unique_events))
        unique_events_in_tree = set(leaves)
        missing_events = len(list(unique_events)) - len(list(unique_events_in_tree))
        duplicated_activities = sum(
            [
                count - 1
                for item, count in collections.Counter(leaves).items()
                if count > 1
            ]
        )
        counter = missing_events + duplicated_activities
        self.simplicity = 1 - counter / denominator
        return all_leaves, unique_events_in_tree

    def count_replay_fitness_precision_generalization(self, trace_frequency, all_leaves):
        denominator = sum(trace_frequency.values())
        counter = 0
        matches = 0
        executions = {str(tree): 0 for tree in all_leaves}
        for trace, val in trace_frequency.items():
            if_match, visited_nodes, executions_list = compare_to_trace(self, trace)
            if if_match:
                matches += val
                logging.info(
                    f"Trace: {trace}, execution list: {executions_list}, all leaves: {all_leaves}, visited nodes: {visited_nodes}, len of trace list: {denominator}"
                )
                counter += (
                    (len(all_leaves) - len(list(visited_nodes))) / len(all_leaves) * val
                )
                for item, count in collections.Counter(
                    [str(t) for t in executions_list]
                ).items():
                    executions[item] += count * val

        self.replay_fitness = matches / denominator
        self.precision = (1 - (counter / denominator)) if counter > 0 else 0
        generalization_counter = 0
        # logging.error(f"Execution list: {executions}")
        for key in executions.keys():
            generalization_counter += (
                pow(math.sqrt(executions[key]), -1) if executions[key] > 0 else 0
            )
        self.generalization = (
            (1 - (generalization_counter / len(all_leaves)))
            if generalization_counter > 0
            else 0
        )

    def count_fitness(
        self,
        unique_events,
        trace_frequency,
        config_params: Config,
    ):
        all_leaves, unique_events_in_tree = self.count_simplicity(unique_events)
        self.count_replay_fitness_precision_generalization(trace_frequency, all_leaves)
        self.fitness = (
            config_params.replay_fitness_weight * self.replay_fitness
            + config_params.simplicity_weight * self.simplicity
            + config_params.precision_weight * self.precision
            + config_params.generalization_weight * self.generalization
        ) / (config_params.replay_fitness_weight + config_params.precision_weight + config_params.simplicity_weight + config_params.generalization_weight)


def create_tree(process_tree: ProcessTree, parent=None):
    label = process_tree.label if process_tree.label else process_tree.operator.value
    tree = Tree(label.replace("->", "→"), parent, None)
    children = [
        create_tree(child_process_tree, tree)
        for child_process_tree in process_tree.children
    ]
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
                    # _i = i
                    start_tree, _i, error, visited_child_nodes = find_next_node(
                        child, i, trace
                    )
                    if not error:
                        children.remove(child)
                        visited_nodes += visited_child_nodes
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
            if not children:
                break
        if children:
            error = True
    elif start_tree.label == "→":
        for child in start_tree.children:
            if child.children:
                start_tree, i, error, visited_child_nodes = find_next_node(
                    child, i, trace
                )
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
                    start_tree, i, error, visited_child_nodes = find_next_node(
                        child, i, trace
                    )
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
            if not children:
                break
        if start_len == len(children):
            error = True
    elif start_tree.label == "X":
        children = list(start_tree.children)
        child_match_len = {}
        for child in children:
            if child.children:
                start_tree, _i, _error, visited_child_nodes = find_next_node(
                    child, i, trace
                )
                if not error:
                    child_match_len[child] = [_i, visited_child_nodes]
            try:
                if child.label == trace[i]:
                    child_match_len[child] = [i + 1, [child]]
            except IndexError:
                pass
            if child.label == "τ":
                child_match_len[child] = [i, []]
        if child_match_len.keys():
            best_match = sorted(child_match_len.items(), key=lambda item: item[1][0])[
                -1
            ]
            i = best_match[1][0]
            visited_nodes += best_match[1][1]
        else:
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
                _, _i, error, visited_child_nodes = find_next_node(
                    start_tree, i, trace
                )
                if not error:
                    i = _i
                    visited_nodes += visited_child_nodes
            elif redo.children and not find_next_node(redo, i, trace)[2]:
                _, _i, error, visited_child_nodes = find_next_node(
                    redo, i, trace
                )
                if not error:
                    i = _i
                    visited_nodes += visited_child_nodes
                    _, _i, error, visited_child_nodes = find_next_node(
                        start_tree, i, trace
                    )
                    if not error:
                        i = _i
                        visited_nodes += visited_child_nodes
            elif len(trace) > i and exit_loop.label == trace[i]:
                i += 1
                visited_nodes.append(exit_loop)
            elif exit_loop.children:
                _, _i, error, visited_child_nodes = find_next_node(
                    exit_loop, i, trace
                )
                if not error:
                    i = _i
                    visited_nodes += visited_child_nodes
            else:
                error = True
        elif do.children:
            _, _i, error, visited_child_nodes = find_next_node(do, i, trace)
            if not error:
                i = _i
                visited_nodes += visited_child_nodes
                if len(trace) > i and redo.label == trace[i]:
                    i += 1
                    visited_nodes.append(redo)
                    _, _i, error, visited_child_nodes = find_next_node(
                        start_tree, i, trace
                    )
                    if not error:
                        i = _i
                        visited_nodes += visited_child_nodes
                elif redo.children and not find_next_node(redo, i, trace)[2]:
                    _, i, error, visited_child_nodes = find_next_node(
                        redo, i, trace
                    )
                    if not error:
                        visited_nodes += visited_child_nodes
                        _, i, error, visited_child_nodes = find_next_node(
                            start_tree, i, trace
                        )
                        if not error:
                            visited_nodes += visited_child_nodes
                elif len(trace) > i and exit_loop.label == trace[i]:
                    i += 1
                    visited_nodes.append(exit_loop)
                elif exit_loop.children:
                    _, _i, error, visited_child_nodes = find_next_node(
                        exit_loop, i, trace
                    )
                    if not error:
                        i = _i
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
