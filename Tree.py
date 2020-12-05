import re
import collections
import logging
from itertools import permutations, chain


# operator_map = {
#     "parallel execution": {"value": "\u02C4", "nodes": 2},
#     "non-exclusive choice": {"value": "\u02C5", "nodes": 2},
#     "exclusive choice": {"value": "x", "nodes": 2},
#     "sequential execution": {"value": "\u2192", "nodes": len(event_list)},
#     "repeated execution": {"value": "\u21BA", "nodes": 3},
# }
class Tree:

    def __init__(self, tree_model):
        self.tree_model = tree_model.replace(" ", "")
        self.tree_regex = None
        self.fitness = None
        self.metrics = {"replay fitness": 0, "precision": 0, "simplicity": 0}
        # self.elite = 0

    def __str__(self):
        return self.tree_model

    def __gt__(self, other):
        return self.fitness > other.fitness

    def create_tree_regex(self):
        regex_parallel = r"([\*X\+O→])\((([^()])*)\)"
        initial_pattern = re.compile(regex_parallel)
        tree_model = self.tree_model
        while True:
            res = initial_pattern.findall(tree_model)
            # print(res)
            for pattern in res:
                sign = pattern[0]
                # print(sign)
                nodes = pattern[1].replace("'", "").split(",")
                # print(nodes)
                if sign == "→":
                    reg = "".join(nodes)  # TODO zmien jak beda normalne dane
                elif sign == "+":
                    perm = permutations(nodes)
                    reg = (
                        "#" + "|".join(["".join(per) for per in list(perm)]) + "@"
                    )  # TODO zmien jak beda normalne dane
                elif sign == "X":
                    reg = f'#{"|".join(nodes)}@'  # TODO zmien jak beda normalne dane
                elif sign == "*":
                    try:
                        args = "".join(nodes[:-1])
                        if args is None:
                            reg = nodes[-1]
                        else:
                            reg = f"#{args}@*{nodes[-1]}"  # TODO zmien jak beda normalne dane
                            # reg = f"#{nodes[0]}{nodes[1]}@*{nodes[2]}"  # TODO zmien jak beda normalne dane
                    except IndexError:
                        reg = ""
                elif sign == "O":
                    perm = []
                    for n in range(2, len(nodes) + 1):
                        perm.append(permutations(nodes, r=n))
                    perm = chain(*perm)
                    reg = "#"
                    for p in perm:
                        reg += "".join(p) + "|"
                    reg = reg.rstrip("|")
                    reg += "|" + "|".join(nodes)
                    reg += "@"
                tree_model = tree_model.replace(pattern[0] + "(" + pattern[1] + ")", reg)
            if len(res) == 0:
                break
        return f"^{tree_model.replace('#', '(').replace('@', ')')}$"

    def count_replay_fitness(self, traces):
        matches = 0
        # logging.info("Tree_regex: " + self.tree_regex)
        # logging.info("Tree model: " + self.tree_model)
        pattern = re.compile(self.tree_regex)
        for trace in traces:
            if pattern.match(trace):
                matches += 1
        self.metrics["replay fitness"] = matches/len(traces)
        return matches, self.metrics["replay fitness"]

    def count_simplicity(self, unique_events):
        # PYTANIE - czy root ma byc liczony jako node !!!!! I czy ta metoda liczenia simplicity jest OK
        model_activities = r"[a-z]"
        matches = re.findall(model_activities, self.tree_model)
        missing_activities = len(unique_events) - len(set(matches))
        duplicated_activities = [item for item, count in collections.Counter(self.tree_model).items() if count > 1]
        duplicated_activities = len(re.findall(model_activities, "".join(duplicated_activities)))
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
            self.metrics["simplicity"] = 1 - counter/denominator
        else:
            self.metrics["simplicity"] = 0
        # print(f"Mianownik: {denominator}")
        return self.metrics["simplicity"]

    def count_precision(self, all_possible_traces, replay_fitness_matches):
        regex = re.compile(self.tree_regex)
        matches = 0
        for permutation in all_possible_traces:
            if regex.match(permutation):
                matches += 1
        self.metrics["precision"] = 1 - ((matches - replay_fitness_matches) / len(all_possible_traces)) # abc bca cab - xor
        return self.metrics["precision"]

    def count_fitness(self, replay_fitness_weight, precision_weight, simplicity_weight, traces, unique_events, all_possible_traces):
        self.tree_regex = self.create_tree_regex()
        matches, replay_fitness = self.count_replay_fitness(traces)
        replay_fitness = replay_fitness * replay_fitness_weight
        precision = self.count_precision(all_possible_traces, matches) * precision_weight
        simplicity = self.count_simplicity(unique_events) * simplicity_weight
        self.fitness = (replay_fitness + precision + simplicity) / (replay_fitness_weight + precision_weight + simplicity_weight)
        return self.fitness





