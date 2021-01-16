import re
import collections
import logging
import regex
import time
import os
import psutil
import sys
import traceback

PROCESS = psutil.Process(os.getpid())
MEGA = 10 ** 6
MEGA_STR = " " * MEGA
# def log_exception(exception: BaseException, expected: bool = True):
#     """Prints the passed BaseException to the console, including traceback.
#
#     :param exception: The BaseException to output.
#     :param expected: Determines if BaseException was expected.
#     """
#     output = "[{}] {}: {}".format('EXPECTED' if expected else 'UNEXPECTED', type(exception).__name__, exception)
#     print(output)
#     exc_type, exc_value, exc_traceback = sys.exc_info()
#     traceback.print_tb(exc_traceback)
#
#
# def print_memory_usage():
#     """Prints current memory usage stats.
#     See: https://stackoverflow.com/a/15495136
#
#     :return: None
#     """
#     total, available, percent, used, free = psutil.virtual_memory()
#     total, available, used, free = total / MEGA, available / MEGA, used / MEGA, free / MEGA
#     proc = PROCESS.memory_info()[1] / MEGA
#     logging.debug(utility.bcolors.OKCYAN + 'process = %s total = %s available = %s used = %s free = %s percent = %s'
#           % (proc, total, available, used, free, percent))


class Tree:
    unique_number = 1

    def __init__(self, tree):
        self.tree = tree
        self.all_children = []
        self.__get_all_children(tree)
        self.tree_model = str(tree).replace(" ", "")
        self.tree_regex = None
        self.fitness = None
        self.metrics = {"replay fitness": 0.0, "precision": 0.0, "simplicity": 0.0}
        # self.elite = 0

    def __str__(self):
        return self.tree_model

    def __gt__(self, other):
        return self.fitness > other.fitness

    def __get_all_children(self, tree):
        for child in tree.children:
            if child.children:
                self.all_children.append(child)
                self.__get_all_children(child)

    def create_tree_regex(self):

        regex_parallel = r"([\*X\+O→])\((([^()])*)\)"
        initial_pattern = re.compile(regex_parallel)
        tree_model = self.tree_model
        # logging.info("tree model:" + tree_model)
        while True:
            res = initial_pattern.findall(tree_model)
            # print(res)
            for pattern in res:
                sign = pattern[0]
                # print(sign)
                nodes = (
                    pattern[1]
                    .replace("'", "")
                    .replace(",τ", "")
                    .replace("τ,", "")
                    .split(",")
                )
                # print(nodes)
                if sign == "→":
                    reg = f"#{'@#'.join(nodes)}@"  # TODO zmien jak beda normalne dane
                elif sign == "+":
                    per = [f"#{node}@" for node in nodes]
                    per2 = ["#"+ re.sub(r"\?P<(gr.[0-9]*)>.*\1&", "?P=\g<1>", node) + "@" for node in nodes]
                    # logging.info([p.replace("#", "(").replace("@", ")") for p in per])
                    # logging.info([p.replace("#", "(").replace("@", ")") for p in per2])
                    name = f"gri{str(Tree.unique_number)}"
                    Tree.unique_number += 1
                    reg = (
                        f"#?=#{'|'.join(per)}@"
                        + "{"
                        + str(len(nodes))
                        + "}@#?!.*#?P<"
                        + f"{name}>.{name}&@#{'|'.join(per2)}@*#?P="
                        + f"{name}@@#{'|'.join(per2)}@"
                        + "{"
                        + str(len(nodes))
                        + "}"
                    )
                    # reg = f"#?:#?P<{name}>{'|'.join(per)}" + r"@@#?!.*#?P=" + name + "@@{" + str(len(nodes)) + "}"
                    # perm = permutations(nodes)
                    # reg = (
                    #     "#" + "|".join(["".join(per) for per in list(perm)]) + "@"
                    # )  # TODO zmien jak beda normalne dane
                    # logging.info(f"I  !!!!!!!!!!!!{reg.replace('#', '(').replace('@', ')')}")
                elif sign == "X":
                    reg = f'#{"@|#".join(nodes)}@'  # TODO zmien jak beda normalne dane
                elif sign == "*":
                    # logging.info(tree_model)
                    try:
                        # logging.info(nodes)
                        args = "@#".join(nodes[:-1])
                        if len(args) == 0:
                            reg = nodes[-1]
                        else:
                            reg = f"##{args}@?@*#{nodes[-1]}@"  # TODO zmien jak beda normalne dane
                            # reg = f"#{nodes[0]}{nodes[1]}@*{nodes[2]}"  # TODO zmien jak beda normalne dane
                    except IndexError:
                        logging.info("Error")
                        reg = ""
                    # logging.info(reg)
                elif sign == "O":
                    per = [f"#{node}@" for node in nodes]
                    per2 = ["#"+ re.sub(r"\?P<(gr.[0-9]*)>.*\1&", "?P=\g<1>", node) + "@" for node in nodes]
                    # logging.info([p.replace("#", "(").replace("@", ")") for p in per])
                    # logging.info([p.replace("#", "(").replace("@", ")") for p in per2])
                    name = f"gro{str(Tree.unique_number)}"
                    Tree.unique_number += 1
                    reg = (
                        f"#?=#{'|'.join(per)}@"
                        + "{0%"
                        + str(len(nodes))
                        + "}@#?!.*#?P<"
                        + f"{name}>.{name}&@#{'|'.join(per2)}@*#?P="
                        + f"{name}@@#{'|'.join(per2)}@"
                        + "{0%"
                        + str(len(nodes))
                        + "}"
                    )
                    # per = [f"#{node}@" for node in nodes]
                    # name = f"gro{str(Tree.unique_number)}"
                    # Tree.unique_number += 1
                    # reg = (
                    #     f"#?P<{name}>#{'|'.join(per)}@{name}"
                    #     + r"&@#?!.*#?P="
                    #     + name
                    #     + "@@{"
                    #     + str(len(nodes))
                    #     + "}"
                    # )
                    # logging.info(f"O  !!!!!!!!!!!!{reg.replace('#', '(').replace('@', ')')}")
                    # perm = []
                    # for n in range(2, len(nodes) + 1):
                    #     perm.append(permutations(nodes, r=n))
                    # perm = chain(*perm)
                    # reg = "#"
                    # for p in perm:
                    #     reg += "".join(p) + "|"
                    # reg = reg.rstrip("|")
                    # reg += "|" + "|".join(nodes)
                    # reg += "@"
                tree_model = tree_model.replace(
                    pattern[0] + "(" + pattern[1] + ")", reg, 1
                )
                # logging.info("Aftyer: " + tree_model)
            if len(res) == 0:
                break
        # logging.info("Return" + f"^{tree_model.replace('#', '(').replace('@', ')')}$")
        tree_model = re.sub("gr.[0-9]*&", "", tree_model)
        return "^({})$".format(tree_model.replace("#", "(").replace("@", ")").replace("&", "").replace("%", ","))

    # def count_replay_fitness(self, traces):
    #     start= time.time()
    #     matches = 0
    #     # logging.info("Tree_regex: " + self.tree_regex)
    #     # logging.info("Tree model: " + self.tree_model)
    #     try:
    #         pattern = regex.compile(self.tree_regex)
    #     except Exception as e:
    #         logging.info(e)
    #         logging.info(self.tree_model)
    #         logging.info(self.tree_regex)
    #     for trace in traces:
    #         match = pattern.match(trace)
    #         if time.time() - start > 10:
    #             logging.info(self.tree_model)
    #         if match:
    #             # logging.info(f"Group: {match.group()} Groups: {match.groups()}" )
    #             # for i in range(match.captures)
    #             # logging.info(f"Captures: {match.captures(3)}")
    #             # counter += visited edges * ((all edges - visited edges) / all edges)
    #             # all_visits += visited edges
    #             matches += 1
    #     # precision  = 1 - (counter / all_visits)
    #     self.metrics["replay fitness"] = matches / len(traces)

        # return matches, self.metrics["replay fitness"]

    def count_simplicity(self, unique_events):
        # PYTANIE - czy root ma byc liczony jako node !!!!! I czy ta metoda liczenia simplicity jest OK
        # TODO skip operators in duplications
        model_activities = r"[a-z]"
        matches = re.findall(model_activities, self.tree_model)
        missing_activities = len(unique_events) - len(set(matches))
        duplicated_activities = [
            item
            for item, count in collections.Counter(self.tree_model).items()
            if count > 1
        ]
        duplicated_activities = len(
            re.findall(model_activities, "".join(duplicated_activities))
        )
        # print(f"Missing activites: {missing_activities}")
        alternations = 0
        loops = 0
        nodes = len(matches)
        for letter in str(self.tree_model):
            if letter == "O":
                alternations += 1
            elif letter == "*":
                loops += 1
            elif letter in ["→", "+", "X", "τ"]:
                nodes += 1
        counter = duplicated_activities + missing_activities + 3 * alternations + loops
        denominator = nodes + alternations + loops
        if 1 - counter / denominator >= 0:
            self.metrics["simplicity"] = 1 - counter / denominator
        else:
            self.metrics["simplicity"] = 0
        # print(f"Mianownik: {denominator}")
        return self.metrics["simplicity"]

    # def count_precision(self, all_possible_traces, replay_fitness_matches):
    #     try:
    #         regex = re.compile(self.tree_regex)
    #     except Exception:
    #         logging.warning(self.tree_model)
    #         logging.warning(self.tree_regex)
    #     matches = 0
    #     for permutation in all_possible_traces:
    #         if regex.match(permutation):
    #             matches += 1
    #     self.metrics["precision"] = 1 - (
    #         (matches - replay_fitness_matches) / len(all_possible_traces)
    #     )  # abc bca cab - xor
    #     # self.metrics["precision"] = 0.3
    #
    #     return self.metrics["precision"]
    def count_rep_and_prec(self, all_possible_traces, traces):
        start = time.time()
        try:
            pattern = re.compile(self.tree_regex)
        except Exception:
            logging.warning(self.tree_model)
            logging.warning(self.tree_regex)
        fitness_matches = 0
        prec_matches = 0
        for permutation in all_possible_traces:
            if time.time() - start > 10:
                logging.info(self.tree_model)
            if pattern.match(permutation):
                if permutation in traces:
                    fitness_matches += 1
                prec_matches += 1
        self.metrics["precision"] = 1 - (
            (prec_matches - fitness_matches) / len(all_possible_traces)
        )  # abc bca cab - xor
        # self.metrics["precision"] = 0.3
        self.metrics["replay fitness"] = fitness_matches / len(traces)
        return self.metrics["precision"], self.metrics["replay fitness"]

    def count_fitness(
        self,
        replay_fitness_weight,
        precision_weight,
        simplicity_weight,
        traces,
        unique_events,
        all_possible_traces,
    ):
        self.tree_regex = self.create_tree_regex()
        # matches, replay_fitness = self.count_replay_fitness(traces)

        precision, replay_fitness = self.count_rep_and_prec(all_possible_traces, traces)
        simplicity = self.count_simplicity(unique_events) * simplicity_weight
        replay_fitness *= replay_fitness_weight
        precision *= precision_weight
        self.fitness = (replay_fitness + precision + simplicity) / (
            replay_fitness_weight + precision_weight + simplicity_weight
        )
        return self.fitness
