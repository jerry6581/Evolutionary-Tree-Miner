import collections
import logging
import os
import random
from copy import deepcopy
from typing import List

import bpmn_python.bpmn_diagram_layouter as layouter
import bpmn_python.bpmn_diagram_rep as diagram
import bpmn_python.bpmn_diagram_visualizer as visualizer
import matplotlib.pyplot as plt
import pandas

from Main import FILE_NAME

from . import Config, InitialPopulation, Tree, find_nodes, find_operator_nodes


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


def get_elite(tree_list: List[Tree], elite_size: float, initial_size: int):
    tree_list.sort(reverse=True)
    elite_list_size = int(initial_size * elite_size)
    elite = [deepcopy(t) for t in tree_list[:elite_list_size]]
    return elite, tree_list[:initial_size]


def random_creation(worst_list, to_change_size, unique_events):
    to_delete_count = round(len(worst_list) * to_change_size)
    worst_list = worst_list[:-to_delete_count]
    population = InitialPopulation(unique_events, to_delete_count)
    worst_list = worst_list + population.trees
    return worst_list


def get_all_nodes(tree: Tree, nodes_list):
    nodes_list.append(tree)
    for child_tree in tree.children:
        get_all_nodes(child_tree, nodes_list)


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
            operator_list = ["v", "X", "∧", "→"]
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
    elif tree.label == "v":
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
    elif tree.label == "∧":
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


def create_bpmn_model(best_tree: Tree):
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
    bpmn_graph.export_xml_file("./", os.path.join("models", f"{FILE_NAME}-final_model.bpmn"))


def create_plot():
    df = pandas.read_csv(os.path.join("csv_data", f"{FILE_NAME}.csv"))
    df = df.groupby(by="Gen_number").mean()
    plt.figure()
    fig = df.plot()
    fig.set_ylabel("Metric Value")
    fig.set_xlabel("Generation")
    fig = fig.get_figure()
    plt.show()
    fig.savefig(os.path.join("plots", f"{FILE_NAME}.png"))


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
    for tree in tree_list:
        flattening_tree(tree)
        tree.count_fitness(
            unique_events, trace_frequency, config_params, traces_options
        )
    try:
        df = pandas.read_csv(os.path.join("csv_data", FILE_NAME + ".csv"))
    except FileNotFoundError:
        d = {"Gen_number": [], "Fitness": [], "Replay_fitness": [], "Precision": [], "Simplicity": [], "Generalization": [], "Tree": []}
        df = pandas.DataFrame(data=d)
    best_tree = sorted(tree_list)[-1]
    for _ in range(config_params.number_of_generations):
        if best_tree.fitness > config_params.stop_condition_replay_fitness:
            logging.info(
                f"Found tree with satisfying replay fitness!: {max(tree_list).fitness}"
            )
            break
        elite_list, worst_list = get_elite(tree_list, config_params.elite_size, config_params.initial_population_size)
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
        tree_list = elite_list + worst_list_after_change
        best_tree = sorted(tree_list)[-1]
        logging.info(
            f"Tree: {best_tree} Replay fitness: {best_tree.replay_fitness} Precision: {best_tree.precision} Simplicity: {best_tree.simplicity} Generalization: {best_tree.generalization} Fitness: {best_tree.fitness} Iteration: {_}"
        )
        df = df.append({"Gen_number": _+1, "Fitness": best_tree.fitness, "Replay_fitness": best_tree.replay_fitness, "Precision": best_tree.precision, "Simplicity": best_tree.simplicity, "Generalization": best_tree.generalization, "Tree": str(best_tree)}, ignore_index=True)

    df.to_csv(os.path.join("csv_data", FILE_NAME + ".csv"), index=False)
    logging.info(f"Number of iterations: {_}")
    create_bpmn_model(best_tree)
    create_plot()
    return best_tree
