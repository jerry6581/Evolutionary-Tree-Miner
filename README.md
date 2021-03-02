# Evolutionary Tree Miner
Algorytm zaimplementowany w ramach pracy inżynierskiej.

### Uruchomienie programu:

- Python 3.8
- pip install -r requirements.txt
- zastąpienie pliku `\pm4py\simulation\tree_generator\variants\ptandloggenerator.py` z biblioteki pm4py przez plik `\setup\ptandloggenerator.py`
- pomoc: `python Main.py --help`
```bash
usage: Main.py [-h] -f EVENT_LOG_FILE -rw REPLAY_FITNESS_WEIGHT -pw PRECISION_WEIGHT -sw SIMPLICITY_WEIGHT -gw GENERALIZATION_WEIGHT -s STOP_CONDITION_REPLAY_FITNESS -r TREES_TO_REPLACE_SIZE -m TREES_TO_MUTATE_SIZE -c TREES_TO_CROSS_SIZE [-e ELITE_SIZE] [-pop INITIAL_POPULATION_SIZE]
               [-gen NUMBER_OF_GENERATIONS]

optional arguments:
  -h, --help            show this help message and exit
  -f EVENT_LOG_FILE, --file_path EVENT_LOG_FILE
                        required
  -rw REPLAY_FITNESS_WEIGHT, --replay_fitness_weight REPLAY_FITNESS_WEIGHT
                        required
  -pw PRECISION_WEIGHT, --precision_weight PRECISION_WEIGHT
                        required
  -sw SIMPLICITY_WEIGHT, --simplicity_weight SIMPLICITY_WEIGHT
                        required
  -gw GENERALIZATION_WEIGHT, --generalization_weight GENERALIZATION_WEIGHT
                        required
  -s STOP_CONDITION_REPLAY_FITNESS, --stop_condition_replay_fitness STOP_CONDITION_REPLAY_FITNESS
                        required
  -r TREES_TO_REPLACE_SIZE, --trees_to_replace_size TREES_TO_REPLACE_SIZE
                        required
  -m TREES_TO_MUTATE_SIZE, --trees_to_mutate_size TREES_TO_MUTATE_SIZE
                        required
  -c TREES_TO_CROSS_SIZE, --trees_to_cross_size TREES_TO_CROSS_SIZE
                        required
  -e ELITE_SIZE, --elite_size ELITE_SIZE
                        optional
  -pop INITIAL_POPULATION_SIZE, --initial_population_size INITIAL_POPULATION_SIZE
                        optional
  -gen NUMBER_OF_GENERATIONS, --number_of_generations NUMBER_OF_GENERATIONS
                        optional
```