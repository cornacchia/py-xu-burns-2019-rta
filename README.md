This script attempts to reproduce the results described in the 2019 paper by H. Xu and A. Burns titled ["A semi-partitioned model for mixed criticality systems"](https://www.sciencedirect.com/science/article/pii/S0164121219300020).

## Requirements
The script runs on [python3](https://www.python.org/download/releases/3.0/) and needs the following additional packages:
* [numpy](https://numpy.org/) -> `pip3 install numpy`
* [matplotlib](https://matplotlib.org/) -> `pip3 install matplotlib`
* [progress](https://pypi.org/project/progress/) -> `pip3 install progress`

## Usage
To launch the script with the default configuration:
```bash
$ cd path/to/script/directory
$ python3 ./run.py
```

The script will run the four tests described in the paper and produce as results four charts which will be saved at a configurable path (cfr. [Configuration](#configuration)).

## Unit tests
To run the unit tests for the RTA algorithms:
```bash
$ cd path/to/script/directory
$ python3 ./test.py
```

## Configuration
The file `config.py` defines some options for the script:
* `CHECK_NO_MIGRATION`, `CHECK_MODEL_1`, etc. defines which models to test
* `RUN_FIRST_TEST`, `RUN_SECOND_TEST`, etc. defines which tests to run
* `FIRST_FIT_BP`, `WORST_FIT_BP` defines which bin-packing algorithm to use
* `RESULTS_DIR` defines where to save the results
* `CORES_MODE_CHANGES` holds the possible sequences of core mode change
* `CORES_NO_MIGRATION`, `CORES_MODEL_1`, etc. defines the configurations used to test the different models

