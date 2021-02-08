import collections
import logging
import random
import re
import time
from typing import List

from algorithm import Tree_old
from algorithm.InitialPopulation import InitialPopulation


def get_elite(tree_list, elite_size):
    tree_list.sort(reverse=True)
    elite_list_size = int(len(tree_list) * elite_size)
    return tree_list[:elite_list_size], tree_list[elite_list_size:]


def random_creation(worst_list, to_change_size, unique_events):
    to_delete_count = round(len(worst_list) * to_change_size)
    # print(to_delete_count)
    worst_list = worst_list[:-to_delete_count]
    population = InitialPopulation(unique_events, to_delete_count)
    population.create_initial_population()
    for t in population.trees:
        tree = Tree_old.Tree(t)
        worst_list.append(tree)
    return worst_list


def select_random_nodes(tree_model):
    open_parent = [i for i, ltr in enumerate(tree_model) if ltr == "("]
    # try:
    index_parent = random.choice(open_parent[1:])
    # except IndexError as e:
    #     print(e)
    #     raise IndexError(e)
    stack_size = 1
    close_index = None
    for i, ch in enumerate(tree_model[index_parent + 1 :]):
        if ch == "(":
            stack_size += 1
        elif ch == ")":
            stack_size -= 1
        if stack_size == 0:
            close_index = i + index_parent
            break
    # return tree_model[index_parent - 1: close_index + 2] if tree_model[close_index + 2] != "," else tree_model[index_parent - 1: close_index + 3]
    return tree_model[index_parent - 1 : close_index + 2]


def crossover(worst_list, to_change_size):
    crossover_count = round(len(worst_list) * to_change_size)
    for _ in range(crossover_count):
        trees_to_swap = random.sample(worst_list, 2)
        try:
            random_node_1 = select_random_nodes(trees_to_swap[0].tree_model)
            random_node_2 = select_random_nodes(trees_to_swap[1].tree_model)
        except IndexError:
            logging.info(
                f"At least one tree contains only root, so this crossover must be omitted: {[trees_to_swap[i].tree_model for i in range(len(trees_to_swap))]}"
            )
            continue

        # print(random_node_1)
        # print(random_node_2)
        # print("Przed zmiana: ")
        # print(trees_to_swap[0])
        # print(trees_to_swap[1])
        trees_to_swap[0].tree_model = trees_to_swap[0].tree_model.replace(
            random_node_1, random_node_2
        )
        trees_to_swap[1].tree_model = trees_to_swap[1].tree_model.replace(
            random_node_2, random_node_1
        )
        # print("Po zmianie: ")
        # print(trees_to_swap[0])
        # print(trees_to_swap[1])


def mutation(worst_list: List[Tree_old.Tree], to_change_size, unique_events):
    operations = [
        "Node changing",
        "Operator changing",
        "Subtree removal",
        "Node addition",
        "Node swapping",
    ]
    # operations = ["Node swapping"]
    mutation_count = round(len(worst_list) * to_change_size)
    to_draw = list(unique_events) + ["τ"]
    operator_list = ["→", "O", "X", "+", "*"]
    for _ in range(mutation_count):
        operation = random.choice(operations)
        tree_to_mutate = random.choice(worst_list)
        model_activities = r"[a-z]"
        matches = re.findall(model_activities, tree_to_mutate.tree_model)
        missing_activities = unique_events - set(matches)
        duplicated_activities = [
            item
            for item, count in collections.Counter(tree_to_mutate.tree_model).items()
            if count > 1
        ]
        duplicated_activities = re.findall(
            model_activities, "".join(duplicated_activities)
        )
        if operation == "Subtree removal":
            # TODO change to tau in or
            # logging.info("Subtree removal")
            # logging.info(tree_to_mutate.tree_model)
            logging.debug(
                bcolors.OKBLUE
                + f"Starting {operation} for {tree_to_mutate.tree_model} before"
                + bcolors.ENDC
            )
            try:
                to_remove = select_random_nodes(tree_to_mutate.tree_model)
            except IndexError:
                logging.info(
                    f"Nothing to remove in this tree, skipping for {str(tree_to_mutate)}"
                )
                continue
            tree_to_mutate.tree_model = (
                tree_to_mutate.tree_model.replace(to_remove, "")
                .replace("(,", "(")
                .replace(",)", ")")
                .replace(",,", ",")
            )
            logging.debug(
                bcolors.OKBLUE
                + f"Starting {operation} for {tree_to_mutate.tree_model} after"
                + bcolors.ENDC
            )
            # logging.info(tree_to_mutate.tree_model)
        elif operation == "Node changing":
            # TODO think about what happen if there are missing activities and no duplicates
            # logging.info("Node changing:" +  tree_to_mutate.tree_model)
            logging.debug(
                bcolors.OKBLUE
                + f"Starting {operation} for {tree_to_mutate.tree_model} before"
                + bcolors.ENDC
            )
            while duplicated_activities:
                to_substitute = random.choice(duplicated_activities)
                indexes_of_duplicates = [
                    pos
                    for pos, char in enumerate(tree_to_mutate.tree_model)
                    if char == to_substitute
                ]
                index_of_to_substitute = random.choice(indexes_of_duplicates)
                duplicated_activities.remove(to_substitute)
                if missing_activities:
                    to_insert = random.choice(list(missing_activities))
                    missing_activities.remove(to_insert)
                else:
                    to_insert = "τ"
                tree_to_mutate.tree_model = (
                    tree_to_mutate.tree_model[:index_of_to_substitute]
                    + to_insert
                    + tree_to_mutate.tree_model[index_of_to_substitute + 1 :]
                )
                # logging.info("Node changing after char: " + tree_to_mutate.tree_model)
            logging.debug(
                bcolors.OKBLUE
                + f"Starting {operation} for {tree_to_mutate.tree_model} after"
                + bcolors.ENDC
            )

        elif operation == "Operator changing":
            logging.debug(
                bcolors.OKBLUE
                + f"Starting {operation} for {tree_to_mutate.tree_model} before"
                + bcolors.ENDC
            )
            reg = r"[\*X\+O→]"
            random_node_match = random.choice(
                list(re.finditer(reg, tree_to_mutate.tree_model))
            )
            random_node_index = random_node_match.start()
            operator_list_new = list(operator_list)
            operator_list_new.remove(random_node_match.group())
            new_operator_node = random.choice(operator_list_new)
            tree_to_mutate.tree_model = (
                tree_to_mutate.tree_model[:random_node_index]
                + new_operator_node
                + tree_to_mutate.tree_model[random_node_index + 1 :]
            )
            # logging.info("Node changing after sign: " + tree_to_mutate.tree_model)
            logging.debug(
                bcolors.OKBLUE
                + f"Starting {operation} for {tree_to_mutate.tree_model} after"
                + bcolors.ENDC
            )
        elif operation == "Node swapping":
            logging.debug(
                bcolors.OKBLUE
                + f"Starting {operation} for {tree_to_mutate.tree_model} before"
                + bcolors.ENDC
            )
            reg = r"[a-zτ]"
            try:
                random_nodes_match = random.choices(
                    list(re.finditer(reg, tree_to_mutate.tree_model)), k=2
                )
            except IndexError:
                continue  # TODO trash this tree
            random_node_index = random_nodes_match[0].start()
            # logging.warning(tree_to_mutate.tree_model + "before")
            tree_to_mutate.tree_model = (
                tree_to_mutate.tree_model[:random_node_index]
                + random_nodes_match[1].group()
                + tree_to_mutate.tree_model[random_node_index + 1 :]
            )
            random_node_index = random_nodes_match[1].start()
            tree_to_mutate.tree_model = (
                tree_to_mutate.tree_model[:random_node_index]
                + random_nodes_match[0].group()
                + tree_to_mutate.tree_model[random_node_index + 1 :]
            )
            # logging.warning(tree_to_mutate.tree_model + "after")
            # elif operation == "Subtree swapping":
            logging.debug(
                bcolors.OKBLUE
                + f"Starting {operation} for {tree_to_mutate.tree_model} after"
                + bcolors.ENDC
            )

        elif operation == "Node addition":
            logging.debug(
                bcolors.OKBLUE
                + f"Starting {operation} for {tree_to_mutate.tree_model} before"
                + bcolors.ENDC
            )
            # print("Node addition")
            if len(missing_activities) > 0:
                new_leaf = f"'{random.choice(list(missing_activities))}',"

                reg = r"[,\(]"
                random_node_index = (
                    random.choice(
                        list(re.finditer(reg, tree_to_mutate.tree_model))
                    ).start()
                    + 1
                )
                tree_to_mutate.tree_model = (
                    tree_to_mutate.tree_model[:random_node_index]
                    + new_leaf
                    + tree_to_mutate.tree_model[random_node_index:]
                )
                logging.debug(
                    bcolors.OKBLUE
                    + f"Starting {operation} for {tree_to_mutate.tree_model} after"
                    + bcolors.ENDC
                )


def flattening_tree(tree_list: List[Tree_old.Tree]):
    # operators_reg = r"[\*X\+O→]"

    operators = "*X+O→"
    for t in tree_list:
        logging.debug(
            bcolors.OKBLUE + f"Starting flattening for {t} before" + bcolors.ENDC
        )
        duplicated_activities = [
            (item, count)
            for item, count in collections.Counter(t.tree_model).items()
            if count > 1
        ]
        logging.debug(
            bcolors.OKBLUE
            + f"Duplicated operators {duplicated_activities}"
            + bcolors.ENDC
        )
        for d in duplicated_activities:
            if d[0] in operators:
                logging.debug(
                    bcolors.OKBLUE + f"Duplicated operators {d[0]}" + bcolors.ENDC
                )
                for n in range(0, d[1]):
                    operator_reg = d[0] if d[0] in "XO→" else r"\{}".format(d[0])
                    # logging.info(operator_reg)
                    for first_duplicate_index in re.finditer(
                        operator_reg, t.tree_model
                    ):
                        first_duplicate_index = first_duplicate_index.start()
                        # logging.info(first_duplicate_index)
                        # first_duplicate_index = t.tree_model.index(d[0])
                        stack_size = 0
                        for i, ch in enumerate(
                            t.tree_model[first_duplicate_index + 1 :]
                        ):
                            if ch == "(":
                                stack_size += 1
                            elif ch == ")":
                                stack_size -= 1
                            if stack_size == 1 and ch == d[0]:
                                # first_duplicate_index + i , first_duplicate_index + i + 1 -> remove
                                inner_stack = 0
                                for j, inner_char in enumerate(
                                    t.tree_model[first_duplicate_index + i + 2 :]
                                ):
                                    if inner_char == "(":
                                        inner_stack += 1
                                    elif inner_char == ")":
                                        inner_stack -= 1
                                    if inner_stack == 0:
                                        close_index = j + first_duplicate_index + i + 2
                                        t.tree_model = (
                                            t.tree_model[
                                                : first_duplicate_index + i + 1
                                            ]
                                            + t.tree_model[
                                                first_duplicate_index
                                                + i
                                                + 3 : close_index
                                            ]
                                            + t.tree_model[close_index + 1 :]
                                        )
                                        # stack_size = 0
                                        break
                                logging.debug(
                                    bcolors.OKBLUE
                                    + f"Starting flattening for {t} after"
                                    + bcolors.ENDC
                                )
                                break


# def test():
#     operators_reg = r"[\*X\+O→]"
#     t = Tree.Tree("+('a',O(O('b','c'),X('e',+('d',X('f','τ')))))")
#     duplicated_activities = [item for item, count in collections.Counter(t.tree_model).items() if
#                              count > 1]
#
#     duplicated_activities = re.findall(operators_reg, "".join(duplicated_activities))
#     print(duplicated_activities)
#     for duplicate in duplicated_activities:
#         first_duplicate_index = t.tree_model.index(duplicate)
#         stack_size = 0
#         for i, ch in enumerate(t.tree_model[first_duplicate_index + 1:]):
#             if ch == "(":
#                 stack_size += 1
#             elif ch == ")":
#                 stack_size -= 1
#             if stack_size == 1 and ch == duplicate:
#                 # first_duplicate_index + i , first_duplicate_index + i + 1 -> remove
#                 inner_stack = 0
#                 for j, inner_char in enumerate(t.tree_model[first_duplicate_index + i + 2:]):
#                     # print(j)
#                     print(inner_char)
#                     if inner_char == "(":
#                         inner_stack += 1
#                     elif inner_char == ")":
#                         inner_stack -= 1
#                     if inner_stack == 0:
#                         close_index = j + first_duplicate_index + i
#                         logging.info(t.tree_model + f"BEFORE !!!! close {close_index}")
#                         tmp = t.tree_model[: first_duplicate_index + i + 1] + t.tree_model[
#                                                                               first_duplicate_index + i + 3: close_index + 2]
#                         logging.info(tmp + "Middle !!!!!!")
#                         t.tree_model = tmp + t.tree_model[close_index + 3 :]
#                         logging.info(t.tree_model + "AFTER !!!!")
#                         break
# if __name__ == "__main__":
#     logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s %(message)s', datefmt='%I:%M:%S', level=logging.INFO)
#     test()
class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def run(
    tree_list,
    unique_events,
    trace_list,
    all_possible_traces,
    nr_generation,
    stop_fitness,
):
    for _ in range(nr_generation):
        start = time.time()
        logging.debug(
            bcolors.WARNING + f"Starting generation {_} at {start}" + bcolors.ENDC
        )
        logging.info(f"Best fitness after {_} generations: {max(tree_list).fitness}")
        elite_list, worst_list = get_elite(tree_list, 0.3)
        logging.debug(
            bcolors.WARNING
            + f"Time after get_elite: {time.time() - start}"
            + bcolors.ENDC
        )
        worst_list_after_change = random_creation(worst_list, 0.3, unique_events)
        logging.debug(
            bcolors.WARNING
            + f"Time after random creation: {time.time() - start}"
            + bcolors.ENDC
        )
        mutation(worst_list_after_change, 0.5, unique_events)
        logging.debug(
            bcolors.WARNING
            + f"Time after mutation: {time.time() - start}"
            + bcolors.ENDC
        )
        crossover(worst_list_after_change, 0.3)
        logging.debug(
            bcolors.WARNING
            + f"Time after crossover: {time.time() - start}"
            + bcolors.ENDC
        )
        flattening_tree(worst_list_after_change)
        logging.debug(
            bcolors.WARNING
            + f"Time after flattening: {time.time() - start}"
            + bcolors.ENDC
        )
        for t in worst_list_after_change:
            t.count_fitness(10, 5, 1, trace_list, unique_events, all_possible_traces)
        logging.debug(
            bcolors.WARNING
            + f"Time after counting fitness: {time.time() - start}"
            + bcolors.ENDC
        )
        if max(tree_list).fitness > stop_fitness:
            logging.info(
                f"Found tree with satisfying replay fitness!: {max(tree_list).fitness}"
            )
            break
        tree_list = elite_list + worst_list_after_change
    return sorted(tree_list)[-15:]
