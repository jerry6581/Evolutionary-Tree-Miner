from InitialPopulation import InitialPopulation
import Tree
import random
from typing import List
import re
import logging
import collections


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
        tree = Tree.Tree(str(t))
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
    for i, ch in enumerate(tree_model[index_parent + 1:]):
        if ch == "(":
            stack_size += 1
        elif ch == ")":
            stack_size -= 1
        if stack_size == 0:
            close_index = i + index_parent
            break
    # return tree_model[index_parent - 1: close_index + 2] if tree_model[close_index + 2] != "," else tree_model[index_parent - 1: close_index + 3]
    return tree_model[index_parent - 1: close_index + 2]


def crossover(worst_list, to_change_size):
    crossover_count = round(len(worst_list) * to_change_size)
    for _ in range(crossover_count):
        trees_to_swap = random.sample(worst_list, 2)
        try:
            random_node_1 = select_random_nodes(trees_to_swap[0].tree_model)
            random_node_2 = select_random_nodes(trees_to_swap[1].tree_model)
        except IndexError:
            logging.info(f"At least one tree contains only root, so this crossover must be omitted: {[trees_to_swap[i].tree_model for i in range(len(trees_to_swap))]}")
            continue

        # print(random_node_1)
        # print(random_node_2)
        # print("Przed zmiana: ")
        # print(trees_to_swap[0])
        # print(trees_to_swap[1])
        trees_to_swap[0].tree_model = trees_to_swap[0].tree_model.replace(random_node_1, random_node_2)
        trees_to_swap[1].tree_model = trees_to_swap[1].tree_model.replace(random_node_2, random_node_1)
        # print("Po zmianie: ")
        # print(trees_to_swap[0])
        # print(trees_to_swap[1])


def mutation(worst_list: List[Tree.Tree], to_change_size, unique_events):
    operations = ["Node changing", "Subtree removal", "Node addition"]
    mutation_count = round(len(worst_list) * to_change_size)
    to_draw = list(unique_events) + ["τ"]
    operator_list = ["→", "O", "X", "+", "*"]
    for _ in range(mutation_count):
        operation = random.choice(operations)
        tree_to_mutate = random.choice(worst_list)
        if operation == "Subtree removal":
            # logging.info("Subtree removal")
            # logging.info(tree_to_mutate.tree_model)
            try:
                to_remove = select_random_nodes(tree_to_mutate.tree_model)
            except IndexError:
                logging.info(
                    f"Nothing to remove in this tree, skipping for {str(tree_to_mutate)}")
                continue
            tree_to_mutate.tree_model = tree_to_mutate.tree_model.replace(to_remove, "").replace("(,", "(").replace(",)", ")")
            # logging.info(tree_to_mutate.tree_model)
        elif operation == "Node changing":

            # logging.info("Node changing:" +  tree_to_mutate.tree_model)
            reg = r"[a-z\*X\+O→τ]"
            random_node_match = random.choice(list(re.finditer(reg, tree_to_mutate.tree_model)))
            random_node_index = random_node_match.start()
            random_node = random_node_match.group()
            if re.match(r"[a-zτ]", random_node):
                new_node = random.choice(to_draw)
                tree_to_mutate.tree_model = tree_to_mutate.tree_model[:random_node_index] + new_node + tree_to_mutate.tree_model[random_node_index + 1:]
                # logging.info("Node changing after char: " + tree_to_mutate.tree_model)
            else:
                new_operator_node = random.choice(operator_list)
                tree_to_mutate.tree_model = tree_to_mutate.tree_model[:random_node_index] + new_operator_node + tree_to_mutate.tree_model[random_node_index + 1:]
                # logging.info("Node changing after sign: " + tree_to_mutate.tree_model)
        elif operation == "Node addition":
            # print("Node addition")
            new_leaf = random.choice(to_draw)
            new_leaf = f"{new_leaf}," if new_leaf == "τ" else f"'{new_leaf}',"
            reg = r"[,\(]"
            random_node_index = random.choice(list(re.finditer(reg, tree_to_mutate.tree_model))).start() + 1
            tree_to_mutate.tree_model = tree_to_mutate.tree_model[:random_node_index] + new_leaf + tree_to_mutate.tree_model[random_node_index:]
        # elif operation == "Flattening tree":


def run(tree_list, unique_events, trace_list, all_possible_traces, nr_generation, stop_fitness):
    for _ in range(nr_generation):
        logging.info(f"Best fitness for {_}: {max(tree_list).fitness}")
        elite_list, worst_list = get_elite(tree_list, 0.3)
        worst_list_after_change = random_creation(worst_list, 0.1, unique_events)
        mutation(worst_list_after_change, 0.3, unique_events)
        crossover(worst_list_after_change, 0.3)

        for t in worst_list_after_change:
            t.count_fitness(10, 5, 1, trace_list, unique_events, all_possible_traces)
        if max(tree_list).fitness > stop_fitness:
            logging.info(f"Found tree with satisfying replay fitness!: {max(tree_list).fitness}")
            break
        tree_list = elite_list + worst_list_after_change
    return sorted(tree_list)[-15:]





