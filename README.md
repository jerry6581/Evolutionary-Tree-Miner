# Evolutionary Tree Miner
Algorytm zaimplementowany w ramach pracy inżynierskiej.

### Wymagania:

- Python 3.8
- pip

### Uruchomienie programu:

- git clone <link>
- cd Evolutionary-Tree-Miner
- pip3 install virtualenv && virtualenv etm && source etm/bin/activate (opcjonalne - linux/mac)
- pip3 install -r requirements.txt
- cp setup/ptandloggenerator.py etm/lib/python3.8/site-packages/pm4py/simulation/tree_generator/variants/ptandloggenerator.py
- Przykładowe uruchomienie programu: `python3 Main.py -f "event_logs/Artificial - Loan Process.xes" -rw 10 -pw 8 -sw 3 -gw 1 -s 0.85 -r 0.2 -m 0.3 -c 0.3 -e 0.1 -pop 200 -gen 500`
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
