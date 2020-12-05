import random
import string

from pm4py.objects.process_tree.process_tree import ProcessTree
from pm4py.objects.process_tree.pt_operator import Operator
from enum import Enum
from pm4py.util import exec_utils


class Parameters(Enum):
    REC_DEPTH = "rec_depth"
    MIN_REC_DEPTH = "min_rec_depth"
    MAX_REC_DEPTH = "max_rec_depth"
    PROB_LEAF = "prob_leaf"
    EVENTS = "events"


# def generate_random_string(N):
#     """
#     Generate a random string
#
#     Parameters
#     -------------
#     N
#         length of the string
#
#     Returns
#     -------------
#     random_string
#         Random string
#     """
#     return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(N))


def get_random_operator():
    """
    Gets a random operator

    Returns
    ------------
    operator
        Operator
    """
    r = random.random()
    if r < 0.2:
        return Operator.SEQUENCE
    elif r < 0.4:
        return Operator.LOOP
    elif r < 0.6:
        return Operator.XOR
    elif r < 0.8:
        return Operator.OR
    else:
        return Operator.PARALLEL


def gen_event(event_list):
    if random.random() < 0.2:
        return "𝜏"
    else:
        elem = random.choice(event_list)
        event_list.remove(elem)
        return elem


def apply(parameters=None):
    """
    Generate a process tree

    Parameters
    ------------
    parameters
        Paramters of the algorithm, including:
            Parameters.REC_DEPTH -> current recursion depth
            Parameters.MIN_REC_DEPTH -> minimum recursion depth
            Parameters.MAX_REC_DEPTH -> maximum recursion depth
            Parameters.PROB_LEAF -> Probability to get a leaf

    Returns
    ------------
    tree
        Process tree
    """
    if parameters is None:
        parameters = {}

    rec_depth = exec_utils.get_param_value(Parameters.REC_DEPTH, parameters, 0)
    min_rec_depth = exec_utils.get_param_value(Parameters.MIN_REC_DEPTH, parameters, 1)
    max_rec_depth = exec_utils.get_param_value(Parameters.MAX_REC_DEPTH, parameters, 3)
    prob_leaf = exec_utils.get_param_value(Parameters.PROB_LEAF, parameters, 0.25)
    unique_events = exec_utils.get_param_value(Parameters.EVENTS, parameters, [])

    next_parameters = {Parameters.REC_DEPTH: rec_depth + 1, Parameters.MIN_REC_DEPTH: min_rec_depth,
                       Parameters.MAX_REC_DEPTH: max_rec_depth,
                       Parameters.PROB_LEAF: prob_leaf,
                       Parameters.EVENTS: unique_events
                       }

    is_leaf = False

    if min_rec_depth <= rec_depth <= max_rec_depth:
        r = random.random()
        if r < prob_leaf:
            is_leaf = True
    elif rec_depth > max_rec_depth and len(unique_events) <= 2:
        is_leaf = True

    if is_leaf:
        current_tree = ProcessTree(label=gen_event(unique_events))
    elif rec_depth == 0:
        current_tree = ProcessTree(operator=Operator.SEQUENCE)
        start = ProcessTree(label=gen_event(unique_events), parent=current_tree)
        current_tree.children.append(start)
        node = apply(parameters=next_parameters)
        node.parent = current_tree
        current_tree.children.append(node)
        end = ProcessTree(label=gen_event(unique_events))
        end.parent = current_tree
        current_tree.children.append(end)
    else:
        o = get_random_operator()

        current_tree = ProcessTree(operator=o)
        if o == Operator.SEQUENCE:
            n_min = 2
            n_max = 6
            selected_n = random.randrange(n_min, n_max)
            for i in range(selected_n):
                try:
                    child = apply(parameters=next_parameters)
                except IndexError:
                    continue
                child.parent = current_tree
                current_tree.children.append(child)
        elif o == Operator.LOOP:
            if len(unique_events) < 3:
                apply(parameters=parameters)
            else:
                do = apply(parameters=next_parameters)
                do.parent = current_tree
                current_tree.children.append(do)
                redo = apply(parameters=next_parameters)
                redo.parent = current_tree
                current_tree.children.append(redo)
                exit = ProcessTree(parent=current_tree)
                current_tree.children.append(exit)
        elif o == Operator.XOR:
            n_min = 2
            n_max = 5
            selected_n = random.randrange(n_min, n_max)
            for i in range(selected_n):
                try:
                    child = apply(parameters=next_parameters)
                except IndexError:
                    continue
                child.parent = current_tree
                current_tree.children.append(child)
        elif o == Operator.OR:
            n_min = 2
            n_max = 4
            selected_n = random.randrange(n_min, n_max)
            for i in range(selected_n):
                try:
                    child = apply(parameters=next_parameters)
                except IndexError:
                    continue
                child.parent = current_tree
                current_tree.children.append(child)
        elif o == Operator.PARALLEL:
            n_min = 2
            n_max = 4
            selected_n = random.randrange(n_min, n_max)
            for i in range(selected_n):
                try:
                    child = apply(parameters=next_parameters)
                except IndexError:
                    continue
                child.parent = current_tree
                current_tree.children.append(child)
    return current_tree
