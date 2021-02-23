from dataclasses import dataclass, field


@dataclass()
class Config:
    event_log_file: str = field(metadata=dict(args=["-f", "--file_path"], help="required"))
    replay_fitness_weight: float = field(
        metadata=dict(args=["-rw", "--replay_fitness_weight"], help="required")
    )
    precision_weight: float = field(metadata=dict(args=["-pw", "--precision_weight"], help="required"))
    simplicity_weight: float = field(metadata=dict(args=["-sw", "--simplicity_weight"], help="required"))
    generalization_weight: float = field(
        metadata=dict(args=["-gw", "--generalization_weight"], help="required")
    )
    stop_condition_replay_fitness: float = field(
        metadata=dict(args=["-s", "--stop_condition_replay_fitness"], help="required")
    )
    trees_to_replace_size: float = field(
        metadata=dict(args=["-r", "--trees_to_replace_size"], help="required")
    )
    trees_to_mutate_size: float = field(
        metadata=dict(args=["-m", "--trees_to_mutate_size"], help="required")
    )
    trees_to_cross_size: float = field(
        metadata=dict(args=["-c", "--trees_to_cross_size"], help="required")
    )
    elite_size: float = field(
        default=0.1, metadata=dict(args=["-e", "--elite_size"], help="optional")
    )
    initial_population_size: int = field(
        default=150, metadata=dict(args=["-pop", "--initial_population_size"], help="optional")
    )
    number_of_generations: int = field(
        default=200, metadata=dict(args=["-gen", "--number_of_generations"], help="optional")
    )
