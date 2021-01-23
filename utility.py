import collections
import logging
import random

from InitialPopulation import InitialPopulation
from TestTree import Tree, find_nodes, find_operator_nodes
from typing import List
import TestTree


def flattening_tree(tree: Tree):
    for children in tree.children:
        if children.label == tree.label and children.label != "*":
            for child in children.children:
                tree.children.append(child)
                child.parent = tree
            tree.children.remove(children)
    for children in tree.children:
        flattening_tree(children)


def get_elite(tree_list: List[Tree], elite_size: float):
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
        tree = TestTree.create_tree(t)
        worst_list.append(tree)
    return worst_list


def get_all_nodes(tree: Tree, nodes_list):
    # cale drzewo tez sie tutaj doda, bedzie trzeba usunac do crossovera
    nodes_list.append(tree)
    for child_tree in tree.children:
        get_all_nodes(child_tree, nodes_list)



def crossover(worst_list, to_change_size):
    # czy krosowac poddrzewa czy tez liscie TODO
    crossover_count = round(len(worst_list) * to_change_size)
    for _ in range(int(crossover_count/2)):
        trees_to_swap = random.sample(worst_list, 2)
        try:
            nodes_list_1 = []
            nodes_list_2 = []
            get_all_nodes(trees_to_swap[0], nodes_list_1)
            get_all_nodes(trees_to_swap[1], nodes_list_2)
            nodes_list_1 = nodes_list_1[1:]
            nodes_list_2 = nodes_list_2[1:]
        except IndexError:
            logging.info(f"At least one tree contains only root, so this crossover must be omitted: {[trees_to_swap[i] for i in range(len(trees_to_swap))]}")
            continue
        node_to_swap_1 = random.choice(nodes_list_1)
        node_to_swap_2 = random.choice(nodes_list_2)
        print(node_to_swap_1)
        print(node_to_swap_2)
        node_to_swap_1.parent.children.insert(node_to_swap_1.parent.children.index(node_to_swap_1), node_to_swap_2)
        node_to_swap_2.parent.children.insert(node_to_swap_2.parent.children.index(node_to_swap_2), node_to_swap_1)
        node_to_swap_1.parent.children.remove(node_to_swap_1)
        node_to_swap_2.parent.children.remove(node_to_swap_2)
        tmp_parent = node_to_swap_1.parent
        node_to_swap_1.parent = node_to_swap_2.parent
        node_to_swap_2.parent = tmp_parent


def mutation(worst_list: List[Tree], to_change_size, unique_events):
    operations = ["Node changing", "Operator changing", "Subtree removal", "Node addition", "Node swapping"]
    # operations = ["Node swapping"]
    mutation_count = round(len(worst_list) * to_change_size)
    for _ in range(mutation_count):
        operation = random.choice(operations)
        tree_to_mutate = random.choice(worst_list)
        if operation == "Node changing":
            leaves = []
            find_nodes(tree_to_mutate, leaves)
            leaves_str = [str(t) for t in leaves]
            missing_leaves = unique_events.difference(set(leaves_str))
            print(f"Missing: {missing_leaves}")
            duplicated_leaves = {}
            checked = set()
            print(leaves)
            for index, tree in enumerate(leaves):
                for tree_2 in leaves[index + 1:]:
                    if tree.label == tree_2.label and tree.label not in checked:
                        if not duplicated_leaves.get(tree.label):
                            duplicated_leaves.setdefault(tree.label, []).append(tree)
                        duplicated_leaves[tree.label].append(tree_2)
                checked.add(tree.label)
            print(f"Duplikaty!!!!: {duplicated_leaves}")
            while duplicated_leaves.keys() and missing_leaves:
                random_key = random.choice(list(duplicated_leaves.keys()))
                random_duplicated_leaf = random.choice(duplicated_leaves[random_key])
                random_missing_leaf = random.choice(list(missing_leaves))
                print(f"duplikat: {random_duplicated_leaf} zamieniamy na {random_missing_leaf}")
                print(f"Before: {tree_to_mutate}")
                random_duplicated_leaf.label = random_missing_leaf
                print(f"After: {tree_to_mutate}")
                print(f"Po zmianie {duplicated_leaves}")
                missing_leaves.remove(random_missing_leaf)
                duplicated_leaves[random_key].remove(random_duplicated_leaf)
                if len(duplicated_leaves[random_key]) == 1:
                    duplicated_leaves.pop(random_key, None)
                    print(duplicated_leaves)
            # TODO pomyslec co ewentualnie mozna tu dodac, narazie jak sa duplikaty i brakujace to zamienia duplikat na missing
        elif operation == "Node addition":
            print("Node addition")
            leaves = []
            find_nodes(tree_to_mutate, leaves)
            leaves_str = [str(t) for t in leaves]
            missing_leaves = unique_events.difference(set(leaves_str))
            print(f"Missing: {missing_leaves}")
            if missing_leaves:
                operators = []
                find_operator_nodes(tree_to_mutate, operators)
                print(operators)
                operators = [o for o in operators if o.label != "*"]
                if operators:
                    node_to_add_child = random.choice(operators)
                    print(f"Node do ktorego bedzie dodany dzieciak: {node_to_add_child}")
                    new_child = Tree(random.choice(list(missing_leaves)), node_to_add_child)
                    print(f"Nowy dzieciak do dodania: {new_child}")
                    node_to_add_child.children.insert(random.randint(0, len(node_to_add_child.children)), new_child)
                    print(tree_to_mutate)
        elif operation == "Operator changing":
            operators = []
            operator_list = ["O", "X", "+", "→"]
            find_operator_nodes(tree_to_mutate, operators)
            operator_to_change = random.choice(operators)
            if len(operator_to_change.children) == 3:
                operator_list.append("*")
            operator_to_change.label = random.choice(operator_list)
        elif operation == "Node swapping":
            all_nodes = []
            get_all_nodes(tree_to_mutate, all_nodes)
            all_nodes = all_nodes[1:]
            nodes_to_swap = random.sample(all_nodes, 2)
            print(f"nodes to swap: {nodes_to_swap}")
            print(f"Tree before: {tree_to_mutate}")
            nodes_to_swap[0].parent.children[nodes_to_swap[0].parent.children.index(nodes_to_swap[0])] = nodes_to_swap[1]
            nodes_to_swap[1].parent.children[nodes_to_swap[1].parent.children.index(nodes_to_swap[1])] = nodes_to_swap[0]
            tmp = nodes_to_swap[0].parent
            nodes_to_swap[0].parent = nodes_to_swap[1].parent
            nodes_to_swap[1].parent = tmp

            print(f"Tree after: {tree_to_mutate}")
        elif operation == "Subtree removal":
            all_nodes = []
            get_all_nodes(tree_to_mutate, all_nodes)
            all_nodes = all_nodes[1:]
            node_to_remove = random.choice(all_nodes)
            if node_to_remove.parent.label != "*" and len(node_to_remove.parent.children) > 2:
                node_to_remove.parent.children.remove(node_to_remove)


# def run():
#     sample_tree = Tree("O", None)
#     sample_sub_tree = Tree("a", sample_tree)
#     sample_sub_tree_2 = Tree("O", sample_tree)
#     sample_tree.children.append(sample_sub_tree)
#     sample_tree.children.append(sample_sub_tree_2)
#     sample_sub_tree_2.children.append(Tree("a", sample_sub_tree_2))
#     sample_sub_sub_tree = Tree("O", sample_sub_tree_2)
#     sample_sub_tree_2.children.append(sample_sub_sub_tree)
#     sample_sub_sub_tree.children.append(Tree("c", sample_sub_sub_tree))
#     sample_sub_sub_tree.children.append(Tree("a", sample_sub_sub_tree))
#     sample_sub_tree_2.children.append(Tree("e", sample_sub_tree_2))
#     sample_tree2 = Tree("O", None)
#     sample_sub_tree = Tree("a", sample_tree2)
#     sample_sub_tree_2 = Tree("O", sample_tree2)
#     sample_tree2.children.append(sample_sub_tree)
#     sample_tree2.children.append(sample_sub_tree_2)
#     sample_sub_tree_2.children.append(Tree("b", sample_sub_tree_2))
#     sample_sub_sub_tree = Tree("O", sample_sub_tree_2)
#     sample_sub_tree_2.children.append(sample_sub_sub_tree)
#     sample_sub_sub_tree.children.append(Tree("c", sample_sub_sub_tree))
#     sample_sub_sub_tree.children.append(Tree("d", sample_sub_sub_tree))
#     sample_sub_tree_2.children.append(Tree("e", sample_sub_tree_2))
#     print(sample_tree)
#     worst_list = [sample_tree, sample_tree2]
#     unique_events = {"a", "b", "c", "d", "e", "f"}
#     mutation(worst_list, 1, unique_events)
#     flattening_tree(sample_tree)
#     print("first  " + str(sample_tree))
#     print("second   " + str(sample_tree2))
#
#     crossover(worst_list , 1)
#     print("first  " + str(sample_tree))
#     print("second   " + str(sample_tree2))
#     sample_tree.count_fitness("abcde", "abdbcbe",10, 5,1,0.1)
#     print(sample_tree.fitness)

def run(tree_list, unique_events, trace_list, nr_generation, stop_fitness):
    for _ in range(nr_generation):
        # start = time.time()
        # logging.debug(bcolors.WARNING + f"Starting generation {_} at {start}" + bcolors.ENDC)
        # logging.info(f"Best fitness after {_} generations: {max(tree_list).fitness}")
        elite_list, worst_list = get_elite(tree_list, 0.3)
        # logging.debug(bcolors.WARNING + f"Time after get_elite: {time.time() - start}" + bcolors.ENDC)
        worst_list_after_change = random_creation(worst_list, 0.3, unique_events)
        # logging.debug(bcolors.WARNING + f"Time after random creation: {time.time() - start}" + bcolors.ENDC)
        mutation(worst_list_after_change, 0.5, unique_events)
        # logging.debug(bcolors.WARNING + f"Time after mutation: {time.time() - start}" + bcolors.ENDC)
        crossover(worst_list_after_change, 0.3)
        # logging.debug(bcolors.WARNING + f"Time after crossover: {time.time() - start}" + bcolors.ENDC)
        # logging.debug(bcolors.WARNING + f"Time after flattening: {time.time() - start}" + bcolors.ENDC)
        for t in worst_list_after_change:
            flattening_tree(t)
            t.count_fitness(unique_events, trace_list, 10, 5, 1, 0.1)
        # logging.debug(bcolors.WARNING + f"Time after counting fitness: {time.time() - start}" + bcolors.ENDC)
        if max(tree_list).fitness > stop_fitness:
            logging.info(f"Found tree with satisfying replay fitness!: {max(tree_list).fitness}")
            break
        tree_list = elite_list + worst_list_after_change
    return sorted(tree_list)[-15:]


# run()

