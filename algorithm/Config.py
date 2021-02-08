from dataclasses import dataclass, field


@dataclass()
class Config:
    replay_fitness_weight: float = field(metadata=dict(args=["-rw", "--replay_fitness_weight"]))
    precision_weight: float = field(metadata=dict(args=["-pw", "--precision_weight"]))
    simplicity_weight: float = field(metadata=dict(args=["-sw", "--simplicity_weight"]))
    generalization_weight: float = field(metadata=dict(args=["-gw", "--generalization_weight"]))
    stop_condition_replay_fitness: float = field(metadata=dict(args=["-s", "--stop_condition_replay_fitness"]))
    trees_to_replace_size: float = field(metadata=dict(args=["-r", "--trees_to_replace_size"]))
    trees_to_mutate_size: float = field(metadata=dict(args=["-m", "--trees_to_mutate_size"]))
    trees_to_cross_size: float = field(metadata=dict(args=["-c", "--trees_to_cross_size"]))
    elite_size: float = field(default=0.1, metadata=dict(args=["-elite", "--elite_size"]))
    initial_population_size: int = field(default=150, metadata=dict(args=["-pop", "--initial_population_size"]))
    number_of_generations: int = field(default=100, metadata=dict(args=["-gen", "--number_of_generations"]))