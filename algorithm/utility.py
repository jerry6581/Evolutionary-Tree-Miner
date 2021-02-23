import collections
import logging
import random
from typing import List
import time
import bpmn_python.bpmn_diagram_layouter as layouter
import bpmn_python.bpmn_diagram_rep as diagram
import bpmn_python.bpmn_diagram_visualizer as visualizer
from memory_profiler import profile

from . import (Config, InitialPopulation, Tree, find_nodes,
               find_operator_nodes)


def flattening_tree(tree: Tree):
    for children in tree.children:
        if children.label == tree.label and children.label != "*":
            tree.children = (
                tree.children[: tree.children.index(children)]
                + children.children
                + tree.children[tree.children.index(children) + 1 :]
            )
            for child in children.children:
                child.parent = tree
    for children in tree.children:
        flattening_tree(children)


def get_elite(tree_list: List[Tree], elite_size: float):
    tree_list.sort(reverse=True)
    elite_list_size = int(len(tree_list) * elite_size)
    return tree_list[:elite_list_size], tree_list[elite_list_size:]


def random_creation(worst_list, to_change_size, unique_events):
    to_delete_count = round(len(worst_list) * to_change_size)
    worst_list = worst_list[:-to_delete_count]
    population = InitialPopulation(unique_events, to_delete_count)
    worst_list = worst_list + population.trees
    return worst_list


def get_all_nodes(tree: Tree, nodes_list):
    # cale drzewo tez sie tutaj doda, bedzie trzeba usunac do crossovera
    nodes_list.append(tree)
    for child_tree in tree.children:
        get_all_nodes(child_tree, nodes_list)


# TODO - dodac do crossoevra wybieranie drzew o lepszych metrykach # czy krosowac poddrzewa czy tez liscie
def crossover(worst_list, to_change_size):
    crossover_count = round(len(worst_list) * to_change_size)
    for _ in range(int(crossover_count / 2)):
        trees_to_swap = random.sample(worst_list, 2)
        try:
            nodes_list_1 = []
            nodes_list_2 = []
            get_all_nodes(trees_to_swap[0], nodes_list_1)
            get_all_nodes(trees_to_swap[1], nodes_list_2)
            nodes_list_1 = nodes_list_1[1:]
            nodes_list_2 = nodes_list_2[1:]
        except IndexError:
            logging.info(
                f"At least one tree contains only root, so this crossover must be omitted: {[trees_to_swap[i] for i in range(len(trees_to_swap))]}"
            )
            continue
        node_to_swap_1 = random.choice(nodes_list_1)
        node_to_swap_2 = random.choice(nodes_list_2)
        node_to_swap_1.parent.children.insert(
            node_to_swap_1.parent.children.index(node_to_swap_1), node_to_swap_2
        )
        node_to_swap_2.parent.children.insert(
            node_to_swap_2.parent.children.index(node_to_swap_2), node_to_swap_1
        )
        node_to_swap_1.parent.children.remove(node_to_swap_1)
        node_to_swap_2.parent.children.remove(node_to_swap_2)
        tmp_parent = node_to_swap_1.parent
        node_to_swap_1.parent = node_to_swap_2.parent
        node_to_swap_2.parent = tmp_parent


def mutation(worst_list: List[Tree], to_change_size, unique_events):
    operations = [
        "Node changing",
        "Operator changing",
        "Subtree removal",
        "Node addition",
        "Node swapping",
    ]
    mutation_count = round(len(worst_list) * to_change_size)
    for _ in range(mutation_count):
        operation = random.choice(operations)
        tree_to_mutate = random.choice(worst_list)
        if operation == "Node changing":
            leaves = []
            find_nodes(tree_to_mutate, leaves)
            leaves_str = [str(t) for t in leaves]
            missing_leaves = unique_events.difference(set(leaves_str))
            duplicated_leaves = {}
            checked = set()
            for index, tree in enumerate(leaves):
                for tree_2 in leaves[index + 1 :]:
                    if tree.label == tree_2.label and tree.label not in checked:
                        if not duplicated_leaves.get(tree.label):
                            duplicated_leaves.setdefault(tree.label, []).append(tree)
                        duplicated_leaves[tree.label].append(tree_2)
                checked.add(tree.label)
            while duplicated_leaves.keys() and missing_leaves:
                random_key = random.choice(list(duplicated_leaves.keys()))
                random_duplicated_leaf = random.choice(duplicated_leaves[random_key])
                random_missing_leaf = random.choice(list(missing_leaves))
                random_duplicated_leaf.label = random_missing_leaf
                missing_leaves.remove(random_missing_leaf)
                duplicated_leaves[random_key].remove(random_duplicated_leaf)
                if len(duplicated_leaves[random_key]) == 1:
                    duplicated_leaves.pop(random_key, None)
            # TODO pomyslec co ewentualnie mozna tu dodac, narazie jak sa duplikaty i brakujace to zamienia duplikat na missing
        elif operation == "Node addition":
            leaves = []
            find_nodes(tree_to_mutate, leaves)
            leaves_str = [str(t) for t in leaves]
            missing_leaves = unique_events.difference(set(leaves_str))
            if missing_leaves:
                operators = []
                find_operator_nodes(tree_to_mutate, operators)
                operators = [o for o in operators if o.label != "*"]
                if operators:
                    node_to_add_child = random.choice(operators)
                    new_child = Tree(
                        random.choice(list(missing_leaves)), node_to_add_child
                    )
                    node_to_add_child.children.insert(
                        random.randint(0, len(node_to_add_child.children)), new_child
                    )
        elif operation == "Operator changing":
            operators = []
            operator_list = ["O", "X", "+", "→"]
            find_operator_nodes(tree_to_mutate, operators)
            operator_to_change = random.choice(operators)
            if len(operator_to_change.children) == 3:
                operator_list.append("*")
            if operator_to_change.label in operator_list:
                operator_list.remove(operator_to_change.label)
            operator_to_change.label = random.choice(operator_list)
        elif operation == "Node swapping":
            all_leaves = []
            find_nodes(tree_to_mutate, all_leaves)
            nodes_to_swap = random.sample(all_leaves, 2)
            index_0 = nodes_to_swap[0].parent.children.index(nodes_to_swap[0])
            index_1 = nodes_to_swap[1].parent.children.index(nodes_to_swap[1])
            nodes_to_swap[0].parent.children[index_0] = nodes_to_swap[1]
            nodes_to_swap[1].parent.children[index_1] = nodes_to_swap[0]
            tmp = nodes_to_swap[0].parent
            nodes_to_swap[0].parent = nodes_to_swap[1].parent
            nodes_to_swap[1].parent = tmp
        elif operation == "Subtree removal":
            all_nodes = []
            get_all_nodes(tree_to_mutate, all_nodes)
            all_nodes = all_nodes[1:]
            node_to_remove = random.choice(all_nodes)
            if (
                node_to_remove.parent.label != "*"
                and len(node_to_remove.parent.children) > 2
            ):
                node_to_remove.parent.children.remove(node_to_remove)


def fill_bpmn_model(tree: Tree, bpmn_graph, previous_id, process_id):
    if tree.label == "X":
        [root, _] = bpmn_graph.add_exclusive_gateway_to_diagram(
            process_id, gateway_name=tree.label
        )
        [root_end, _] = bpmn_graph.add_exclusive_gateway_to_diagram(
            process_id, gateway_name=tree.label
        )
        bpmn_graph.add_sequence_flow_to_diagram(process_id, previous_id, root, "s")
        for child in tree.children:
            task = fill_bpmn_model(child, bpmn_graph, root, process_id)
            bpmn_graph.add_sequence_flow_to_diagram(process_id, task, root_end, "s")
        return root_end
    elif tree.label == "O":
        [root, _] = bpmn_graph.add_inclusive_gateway_to_diagram(
            process_id, gateway_name=tree.label
        )
        [root_end, _] = bpmn_graph.add_inclusive_gateway_to_diagram(
            process_id, gateway_name=tree.label
        )
        bpmn_graph.add_sequence_flow_to_diagram(process_id, previous_id, root, "s")
        for child in tree.children:
            task = fill_bpmn_model(child, bpmn_graph, root, process_id)
            bpmn_graph.add_sequence_flow_to_diagram(process_id, task, root_end, "s")
        return root_end
    elif tree.label == "+":
        [root, _] = bpmn_graph.add_parallel_gateway_to_diagram(
            process_id, gateway_name=tree.label
        )
        [root_end, _] = bpmn_graph.add_parallel_gateway_to_diagram(
            process_id, gateway_name=tree.label
        )
        bpmn_graph.add_sequence_flow_to_diagram(process_id, previous_id, root, "s")
        for child in tree.children:
            task = fill_bpmn_model(child, bpmn_graph, root, process_id)
            bpmn_graph.add_sequence_flow_to_diagram(process_id, task, root_end, "s")
        return root_end
    elif tree.label == "→":
        for child in tree.children:
            task = fill_bpmn_model(child, bpmn_graph, previous_id, process_id)
            previous_id = task
        return previous_id
    elif tree.label == "*":
        [root, _] = bpmn_graph.add_exclusive_gateway_to_diagram(
            process_id, gateway_name="root"
        )
        bpmn_graph.add_sequence_flow_to_diagram(
            process_id, previous_id, root, "start_to_one"
        )
        task = fill_bpmn_model(tree.children[0], bpmn_graph, root, process_id)
        [root_end, _] = bpmn_graph.add_exclusive_gateway_to_diagram(
            process_id, gateway_name=tree.label
        )
        bpmn_graph.add_sequence_flow_to_diagram(process_id, task, root_end, "s")
        task = fill_bpmn_model(tree.children[1], bpmn_graph, root_end, process_id)
        bpmn_graph.add_sequence_flow_to_diagram(process_id, task, root, "s")
        task = fill_bpmn_model(tree.children[2], bpmn_graph, root_end, process_id)
        return task
    else:
        [task, _] = bpmn_graph.add_task_to_diagram(process_id, task_name=tree.label)
        bpmn_graph.add_sequence_flow_to_diagram(process_id, previous_id, task, "s")
        return task


def create_bpmn_model(best_tree: Tree, time_now):
    bpmn_graph = diagram.BpmnDiagramGraph()
    bpmn_graph.create_new_diagram_graph(diagram_name="Final model")
    process_id = bpmn_graph.add_process_to_diagram()
    [start_id, _] = bpmn_graph.add_start_event_to_diagram(
        process_id, start_event_name="START"
    )
    root_end = fill_bpmn_model(best_tree, bpmn_graph, start_id, process_id)
    [end_id, _] = bpmn_graph.add_end_event_to_diagram(process_id, end_event_name="END")
    bpmn_graph.add_sequence_flow_to_diagram(process_id, root_end, end_id, "s")
    layouter.generate_layout(bpmn_graph)
    visualizer.visualize_diagram(bpmn_graph)
    bpmn_graph.export_xml_file("./", f"{time_now}-final_model.bpmn")

    # visualizer.bpmn_diagram_to_png(bpmn_graph, "diagram")
    # visualizer.bpmn_diagram_to_dot_file(bpmn_graph, "diagram")


def create_test_tree():
    trees = []
    # s1 = Tree("X", None)
    # s2 = Tree("X", s1)
    # s1.children.append(s2)
    # s1.children.append(Tree("b", s1))
    # s2.children.append(Tree("c", s2))
    # s2.children.append(Tree("d", s2))
    # Fig 9
    s1 = Tree("→", None)
    s2 = Tree("→", s1)
    s3 = Tree("→", s1)
    s1.children.append(s2)
    s1.children.append(s3)
    s2.children.append(Tree("a", s2))
    s4 = Tree("O", s2)
    s2.children.append(s4)
    s4.children.append(Tree("b", s4))
    s5 = Tree("O", s4)
    s4.children.append(s5)
    s5.children.append(Tree("c", s5))
    s5.children.append(Tree("d", s5))
    s6 = Tree("X", s3)
    s3.children.append(s6)
    s3.children.append(Tree("g", s3))
    s6.children.append(Tree("e", s6))
    s6.children.append(Tree("f", s6))
    trees.append(s1)
    # Fig 5
    # s1 = Tree("→", None)
    # s2 = Tree("→", s1)
    # s3 = Tree("→", s1)
    # s1.children.append(s2)
    # s1.children.append(s3)
    # s2.children.append(Tree("a", s2))
    # s4 = Tree("+", s2)
    # s2.children.append(s4)
    # s4.children.append(Tree("b", s4))
    # s5 = Tree("+", s4)
    # s4.children.append(s5)
    # s5.children.append(Tree("c", s5))
    # s5.children.append(Tree("d", s5))
    # s6 = Tree("X", s3)
    # s3.children.append(s6)
    # s3.children.append(Tree("g", s3))
    # s6.children.append(Tree("e", s6))
    # s6.children.append(Tree("f", s6))

    # Fig 7
    # s1 = Tree("→", None)
    # s2 = Tree("a", s1)
    # s3 = Tree("+", s1)
    # s1.children.append(s2)
    # s1.children.append(s3)
    # s3.children.append(Tree("d", s3))
    # s4 = Tree("→", s3)
    # s3.children.append(s4)
    # # s4.children.append(Tree("b", s4))
    # s5 = Tree("+", s4)
    # s5.children.append(Tree("b", s5))
    # s5.children.append(Tree("c", s5))
    # s4.children.append(s5)
    # s6 = Tree("→", s4)
    # s4.children.append(s6)
    # s7 = Tree("X", s6)
    # s7.children.append(Tree("e", s7))
    # s7.children.append(Tree("f", s7))
    # s6.children.append(s7)
    # s6.children.append(Tree("g", s6))

    # Fig 6
    # s1 = Tree("→", None)
    # s2 = Tree("→", s1)
    # s3 = Tree("→", s1)
    # s1.children.append(s2)
    # s1.children.append(s3)
    # s2.children.append(Tree("a", s2))
    # s4 = Tree("O", s2)
    # s2.children.append(s4)
    # s4.children.append(Tree("b", s4))
    # s5 = Tree("O", s4)
    # s4.children.append(s5)
    # s5.children.append(Tree("c", s5))
    # s7 = Tree("*", s5)
    # s5.children.append(s7)
    # s7.children.append(Tree("d", s7))
    # s7.children.append(Tree("d", s7))
    # s7.children.append(Tree("z", s7))
    # s6 = Tree("X", s3)
    # s3.children.append(s6)
    # s3.children.append(Tree("g", s3))
    # s6.children.append(Tree("e", s6))
    # s6.children.append(Tree("f", s6))

    # Fig 8
    # s1 = Tree("→", None)
    # s2 = Tree("→", s1)
    # s3 = Tree("→", s1)
    # s1.children.append(s2)
    # s1.children.append(s3)
    # s2.children.append(Tree("a", s2))
    # s4 = Tree("X", s2)
    # s2.children.append(s4)
    # s7 = Tree("+", s4)
    # # s4.children.append(s7)
    # s7.children.append(Tree("b", s7))
    # s7.children.append(Tree("c", s7))
    #
    # s8 = Tree("+", s4)
    # s4.children.append(s7)
    # s4.children.append(s8)
    # s9 = Tree("+", s8)
    # s8.children.append(s9)
    # s9.children.append(Tree("b", s9))
    # s9.children.append(Tree("c", s9))
    # s8.children.append(Tree("d", s8))
    # s9 = Tree("X", s3)
    # s3.children.append(s9)
    # s9.children.append(Tree("e", s9))
    # s9.children.append(Tree("f", s9))
    # s3.children.append(Tree("g", s3))

    # Loop test
    # s1 = Tree("*", None)
    # s1.children.append(Tree("A", s1))
    # s1.children.append(Tree("B", s1))
    # s1.children.append(Tree("C", s1))
    # trees.append([s1, 3])
    #
    # s1 = Tree("*", None)
    # s2 = Tree("O", s1)
    # s2.children.append(Tree("A", s2))
    # s2.children.append(Tree("D", s2))
    # s1.children.append(s2)
    # s1.children.append(Tree("B", s1))
    # s1.children.append(Tree("C", s1))
    # trees.append([s1, 4])
    #
    # s1 = Tree("*", None)
    # s2 = Tree("O", s1)
    # s2.children.append(Tree("B", s2))
    # s2.children.append(Tree("D", s2))
    # s1.children.append(Tree("A", s1))
    # s1.children.append(s2)
    # s1.children.append(Tree("C", s1))
    # trees.append([s1, 4])
    #
    # s1 = Tree("*", None)
    # s2 = Tree("O", s1)
    # s2.children.append(Tree("C", s2))
    # s2.children.append(Tree("D", s2))
    # s1.children.append(Tree("A", s1))
    # s1.children.append(Tree("B", s1))
    # s1.children.append(s2)
    #
    # trees.append([s1, 4])
    #
    # s1 = Tree("*", None)
    # s1.children.append(Tree("A", s1))
    # s1.children.append(Tree("τ", s1))
    # s1.children.append(Tree("C", s1))
    #
    #
    # trees.append([s1, 2])
    #
    # s1 = Tree("*", None)
    # s2 = Tree("O", s1)
    # s2.children.append(Tree("B", s2))
    # s2.children.append(Tree("τ", s2))
    # s1.children.append(Tree("A", s1))
    # s1.children.append(s2)
    # s1.children.append(Tree("C", s1))
    #
    #
    # trees.append([s1, 4])
    #
    # s1 = Tree("*", None)
    # s1.children.append(Tree("A", s1))
    # s1.children.append(Tree("B", s1))
    # s1.children.append(Tree("τ", s1))
    #
    #
    # trees.append([s1, 0])
    #
    # s1 = Tree("*", None)
    # s1.children.append(Tree("τ", s1))
    # s1.children.append(Tree("B", s1))
    # s1.children.append(Tree("C", s1))
    #
    #
    # trees.append([s1, 0])

    return trees


# TODO dodac liczenie metryk po kazdej mutacji lub gdy drzewo wzielo udzial w mutacji to zeby nie bralo kolejny raz w danej generacji !!
def run(tree_list, unique_events, trace_list, config_params: Config):
    logging.info(tree_list)
    trace_frequency = {
        item: count for item, count in collections.Counter(trace_list).items()
    }
    logging.info(f"Trace frequency: {trace_frequency}")
    traces_options = {}
    for trace in trace_frequency.keys():
        for i in range(len(trace)):
            traces_options.setdefault(trace[:i], set()).add(trace[i])
    # logging.info(trace_frequency.keys())
    # logging.info(traces_options.keys())
    # tree_list[0].count_fitness(unique_events, trace_frequency, config_params, traces_options)
    # char_frequency = {char: 0 for char in list(unique_events)}
    # for trace, value in trace_frequency.items():
    #     for item, count in collections.Counter(trace).items():
    #         char_frequency[item] += count * value
    # print(f"Char frequency: {char_frequency}")
    # denominator_generalization = sum([ math.pow(math.sqrt(val), -1) for val in char_frequency.values()])
    for tree in tree_list:
        tree.count_fitness(
            unique_events, trace_frequency, config_params, traces_options
        )
    for _ in range(config_params.number_of_generations):

        elite_list, worst_list = get_elite(tree_list, config_params.elite_size)
        worst_list_after_change = random_creation(
            worst_list, config_params.trees_to_replace_size, unique_events
        )
        mutation(
            worst_list_after_change, config_params.trees_to_mutate_size, unique_events
        )
        crossover(worst_list_after_change, config_params.trees_to_cross_size)
        for t in worst_list_after_change:
            flattening_tree(t)
            t.count_fitness(
                unique_events, trace_frequency, config_params, traces_options
            )
        # logging.info(
        #     f"Stop condition {config_params.stop_condition_replay_fitness}  {_}"
        # )
        if max(tree_list).fitness > config_params.stop_condition_replay_fitness:
            logging.info(
                f"Found tree with satisfying replay fitness!: {max(tree_list).fitness}"
            )
            break
        tree_list = elite_list + worst_list_after_change
    logging.info(f"Number of iterations: {_}")
    # TODO zmienic zeby zwracalo tlyko elite
    return sorted(tree_list)[-15:]
