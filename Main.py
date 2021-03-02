import logging
import os
import time

from argparse_dataclass import ArgumentParser

from algorithm import Config, ImportData, InitialPopulation, utility

FILE_NAME = str(time.time())
logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    datefmt="%I:%M:%S",
    level=logging.INFO,
    handlers=[
        logging.FileHandler(os.path.join("logs", FILE_NAME + ".log"), encoding='UTF-8'),
        logging.StreamHandler()
    ]
)


def start(config_params: Config):
    start_time = time.time()
    log = ImportData(config_params.event_log_file)
    logging.info(log.trace_list)
    logging.info(log.unique_events)
    logging.info(log.event_map)
    population = InitialPopulation(
        log.unique_events, config_params.initial_population_size
    )
    best_tree = utility.run(
        population.trees, log.unique_events, log.trace_list, config_params
    )
    logging.info(f"Execution time: {time.time() - start_time}")
    logging.info(
        f"Tree: {best_tree} Replay fitness: {best_tree.replay_fitness} Precision: {best_tree.precision} Simplicity: {best_tree.simplicity} Generalization: {best_tree.generalization} Fitness: {best_tree.fitness}"
    )
    for k, v in config_params.__dict__.items():
        logging.info(f"{k}: {v}")
    logging.info("Tree class values")
    for k, v in best_tree.__dict__.items():
        logging.info(f"{k}: {v}")


if __name__ == "__main__":
    parser = ArgumentParser(Config)
    config = parser.parse_args()
    start(config)



