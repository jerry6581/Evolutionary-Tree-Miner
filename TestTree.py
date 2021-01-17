import collections
from typing import List, Any
from pm4py.objects.process_tree.process_tree import ProcessTree
import logging


class Tree:
    def __init__(self, label: str, parent: "Tree", children: List["Tree"] = None):
        self.parent = parent
        self.label = label
        self.children = children if children else []
        self.replay_fitness = None
        self.simplicity = None
        self.precision = None

    def __repr__(self):
        return str(self)

    def __str__(self):
        if self.children:
            children = ",".join([str(child) for child in self.children])
            return f"{self.label}({children})"
        else:
            return self.label

    def count_simplicity(self, unique_events):
        leaves = []
        find_nodes(self, leaves)
        leaves = [str(t) for t in leaves if str(t) != 'τ']
        # leaves = list(filter('τ'.__ne__, leaves))
        print(f"Leaves: {leaves}")
        denominator = len(leaves) + len(list(unique_events))
        unique_events_in_tree = set(leaves)
        print(f"Unique events in tree: {unique_events_in_tree}")
        missing_events = len(list(unique_events)) - len(list(unique_events_in_tree))
        print(f"Missing: {missing_events}")
        duplicated_activities = sum([count - 1 for item, count in collections.Counter(leaves).items() if
                                 count > 1])
        print(f"Duplicated: {duplicated_activities}")
        counter = missing_events + duplicated_activities
        self.simplicity = 1 - counter/denominator
        print(f"Simplicity: {self.simplicity}")

    def count_replay_fitness(self, trace_list):
        matches = 0
        for trace in trace_list:
            if compare_to_trace(self, trace):
                matches += 1
        self.replay_fitness = matches / len(trace_list)

    def count_precision(self, trace_list):


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





# τ
def find_next_node(start_tree, i, trace):
    error = False
    if start_tree.label == "+":
        children = list(start_tree.children)
        for _ in range(len(children)):
            for child in children:
                if child.children:
                    _i = i
                    start_tree, i, error = find_next_node(child, i, trace)
                    if not error:
                        children.remove(child)
                    else:
                        i = _i
                try:
                    if child.label == trace[i]:
                        children.remove(child)
                        i += 1
                except IndexError:
                    logging.debug("Trace is too short to validate against this tree.")
                if child.label == "τ":
                    children.remove(child)
            if not children: break
        if children: error = True
    elif start_tree.label == "→":
        for child in start_tree.children:
            if child.children:
                start_tree, i, error = find_next_node(child, i, trace)
                if not error:
                    continue
                else:
                    error = True
                    break

            if len(trace) > i and child.label == trace[i]:
                i += 1
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
                    start_tree, i, error = find_next_node(child, i, trace)
                    if not error:
                        children.remove(child)
                    else:
                        i = _i  # bo jak find_next_node zwroci blad to sie chcemy sie przesuwac w trace wiec wracamy
                try:
                    if child.label == trace[i]:
                        children.remove(child)
                        i += 1
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
                    start_tree, i, error = find_next_node(child, i, trace)
                    if not error:
                        children.remove(child)
                    else:
                        i = _i
                try:
                    if child.label == trace[i]:
                        children.remove(child)
                        i += 1
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
            if len(trace) > i and redo.label == trace[i]:
                i += 1
                start_tree, i, error = find_next_node(start_tree, i, trace)
            elif redo.children and not find_next_node(redo, i, trace)[2]:
                save_tree = start_tree
                start_tree, i, error = find_next_node(redo, i, trace)
                if not error:
                    start_tree, i, error = find_next_node(save_tree, i, trace)
            elif len(trace) > i and exit_loop.label == trace[i]:
                i += 1
            elif exit_loop.children:
                _i = i
                start_tree, i, error = find_next_node(exit_loop, i, trace)
                if error:
                    i = _i
            else:
                error = True
        elif do.children:
            save_tree = start_tree
            start_tree, i, error = find_next_node(do, i, trace)
            if not error:
                if len(trace) > i and redo.label == trace[i]:
                    i += 1
                    start_tree, i, error = find_next_node(save_tree, i, trace)
                elif redo.children and not find_next_node(redo, i, trace)[2]:
                    save_tree = save_tree
                    start_tree, i, error = find_next_node(redo, i, trace)
                    if not error:
                        start_tree, i, error = find_next_node(save_tree, i, trace)
                elif len(trace) > i and exit_loop.label == trace[i]:
                    i += 1
                elif exit_loop.children:
                    _i = i
                    start_tree, i, error = find_next_node(exit_loop, i, trace)
                    if error:
                        i = _i
                else:
                    error = True
        else:
            error = True

    return start_tree, i, error



def compare_to_trace(start_tree: Tree, trace: str):
    start_tree, i, error = find_next_node(start_tree, 0, trace)
    if i != len(trace):
        error = True
    return not error


#     if tree.label == "O":
#         for child in tree.children:
#
#         possible_char =


sample_tree = Tree("O", None)
sample_sub_tree = Tree("a", sample_tree)
sample_sub_tree_2 = Tree("*", sample_tree)
sample_tree.children.append(sample_sub_tree)
sample_tree.children.append(sample_sub_tree_2)
sample_sub_tree_2.children.append(Tree("b", sample_sub_tree_2))
sample_sub_sub_tree = Tree("X", sample_sub_tree_2)
sample_sub_tree_2.children.append(sample_sub_sub_tree)
sample_sub_sub_tree.children.append(Tree("c", sample_sub_sub_tree))
sample_sub_sub_tree.children.append(Tree("τ", sample_sub_sub_tree))
sample_sub_tree_2.children.append(Tree("c", sample_sub_tree_2))

print(sample_tree)

# print(find_node(sample_tree, "d"))
t = str(sample_tree)
print("abcbdbe")
print(compare_to_trace(sample_tree, "abcbdbe"))
unique_events = {"a", "b", "c", "d", "e"}
sample_tree.count_simplicity(unique_events)
# tree_list = []
# find_nodes(sample_tree, tree_list)
# print(tree_list)