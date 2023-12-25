import collections
import logging
import math
from typing import List

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

    def count_precision(self, unique_events, traces_options):
        escaping_edges = {}
        for partial_trace, options in traces_options.items():
            possible_partial_trace = [
                partial_trace + activity
                for activity in list(unique_events)
                if activity not in traces_options[partial_trace]
            ]
            for sub_trace in possible_partial_trace:
                match_mask = [False for _ in list(unique_events)]
                check_next_node(self, 0, sub_trace, match_mask)
                if len(sub_trace) == sum(match_mask):
                    escaping_edges.setdefault(partial_trace, set()).add(sub_trace[-1])
        escaping_edges_count = sum([len(_) for _ in escaping_edges.values()])
        if escaping_edges_count:
            self.precision = 1 - (
                escaping_edges_count / (sum([len(_) for _ in traces_options.values()]) + sum([len(_) for _ in escaping_edges.values()]))
            )
        else:
            self.precision = 0

    def count_replay_fitness_and_generalization(self, trace_frequency, all_leaves):
        denominator = sum(trace_frequency.values())
        counter = 0
        matches = 0
        executions = {str(tree): 0 for tree in all_leaves}
        for trace, val in trace_frequency.items():
            if_match, visited_nodes, executions_list = compare_to_trace(self, trace)
            if if_match:
                matches += val
                counter += (
                    (len(all_leaves) - len(list(visited_nodes))) / len(all_leaves) * val
                )
                for item, count in collections.Counter(
                    [str(t) for t in executions_list]
                ).items():
                    executions[item] += count * val

        self.replay_fitness = matches / denominator
        generalization_counter = 0
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
        self, unique_events, trace_frequency, config_params: Config, traces_options
    ):
        all_leaves, unique_events_in_tree = self.count_simplicity(unique_events)
        self.count_replay_fitness_and_generalization(trace_frequency, all_leaves)
        self.count_precision(unique_events, traces_options)
        self.fitness = (
            config_params.replay_fitness_weight * self.replay_fitness
            + config_params.simplicity_weight * self.simplicity
            + config_params.precision_weight * self.precision
            + config_params.generalization_weight * self.generalization
        ) / (
            config_params.replay_fitness_weight
            + config_params.precision_weight
            + config_params.simplicity_weight
            + config_params.generalization_weight
        )


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


def update_mask(i, match_mask):
    for i in range(i):
        try:
            match_mask[i] = True
        except Exception:
            break


def check_next_node(start_tree, i, trace, match_mask):
    visited_nodes = list()
    error = False
    if start_tree.label == "∧":
        children = list(start_tree.children)
        for _ in range(len(children)):
            for child in children:
                if child.children:
                    _, _i, error, visited_child_nodes = check_next_node(
                        child, i, trace, match_mask
                    )
                    if not error:
                        children.remove(child)
                        visited_nodes += visited_child_nodes
                        i = _i
                        update_mask(i, match_mask)
                try:
                    if child.label == trace[i]:
                        children.remove(child)
                        i += 1
                        update_mask(i, match_mask)
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
                _, i, error, visited_child_nodes = check_next_node(
                    child, i, trace, match_mask
                )
                if not error:
                    visited_nodes += visited_child_nodes
                    update_mask(i, match_mask)
                    continue
                else:
                    error = True
                    break

            if len(trace) > i and child.label == trace[i]:
                i += 1
                update_mask(i, match_mask)
                visited_nodes.append(child)
            elif child.label == "τ":
                pass
            else:
                error = True
                break
    elif start_tree.label == "v":
        children = list(start_tree.children)
        start_len = len(children)
        for _ in range(len(children)):
            for child in children:
                if child.children:
                    _, _i, _error, visited_child_nodes = check_next_node(
                        child, i, trace, match_mask
                    )
                    if not _error:
                        children.remove(child)
                        visited_nodes += visited_child_nodes
                        i = _i
                        update_mask(i, match_mask)
                try:
                    if child.label == trace[i]:
                        children.remove(child)
                        i += 1
                        update_mask(i, match_mask)
                        visited_nodes.append(child)
                except IndexError:
                    pass
                if child.label == "τ":
                    children.remove(child)
            if not children:
                break
        if start_len == len(children):
            error = True
    elif start_tree.label == "X":
        children = list(start_tree.children)
        child_match_len = {}
        for child in children:
            if child.children:
                _, _i, _error, visited_child_nodes = check_next_node(
                    child, i, trace, match_mask
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
            update_mask(i, match_mask)
        else:
            error = True
    elif start_tree.label == "*":
        do = start_tree.children[0]
        redo = start_tree.children[1]
        if len(start_tree.children) > 2:
            exit_loop = start_tree.children[2]
        if len(trace) > i and do.label == trace[i]:
            i += 1
            update_mask(i, match_mask)
            visited_nodes.append(do)
        elif do.children:
            _, _i, error, visited_child_nodes = check_next_node(
                do, i, trace, match_mask
            )
            if error or i == _i:
                return start_tree, i, error, visited_nodes
            i = _i
            update_mask(i, match_mask)
            visited_nodes += visited_child_nodes
        else:
            return start_tree, i, True, visited_nodes

        i_before_redo = i
        redo_error = False
        if len(trace) > i and redo.label == trace[i]:
            i += 1
            update_mask(i, match_mask)
            visited_nodes.append(redo)
        elif redo.children:
            _, _i, error, visited_child_nodes = check_next_node(
                redo, i, trace, match_mask
            )
            if not error:
                i = _i
                update_mask(i, match_mask)
                visited_nodes += visited_child_nodes
            else:
                redo_error = True
        elif redo.label != "τ":
            redo_error = True
        if i == i_before_redo:
            error = True
            if len(trace) <= i:
                pass
            elif exit_loop.label == trace[i]:
                i += 1
                update_mask(i, match_mask)
                visited_nodes.append(exit_loop)
                error = False
            elif exit_loop.children:
                _, _i, error, visited_child_nodes = check_next_node(
                    exit_loop, i, trace, match_mask
                )
                if i == _i:
                    return start_tree, i, True, visited_nodes
                if not error:
                    i = _i
                    update_mask(i, match_mask)
                    visited_nodes += visited_child_nodes
            elif exit_loop.label == "τ":
                return start_tree, i, True, visited_nodes
            if not error:
                return start_tree, i, error, visited_nodes
            if redo_error:
                return start_tree, i, redo_error, visited_nodes

        if (error or i != i_before_redo) and not redo_error:
            _, _i, error, visited_child_nodes = check_next_node(
                start_tree, i, trace, match_mask
            )
            if not error:
                i = _i
                update_mask(i, match_mask)
                visited_nodes += visited_child_nodes

    return start_tree, i, error, visited_nodes


def compare_to_trace(start_tree: Tree, trace: str):
    start_tree, i, error, visited_nodes = check_next_node(start_tree, 0, trace, None)
    if i != len(trace):
        error = True
    visited_nodes = visited_nodes if not error else set()
    visited_nodes_set = set(visited_nodes)
    return not error, visited_nodes_set, visited_nodes
