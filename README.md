# Boolean Network Reconstruction

This is the repository for the Statistical Data Analysis Project for 2025/26 SDA Bioinformatics course @ MIMUW.

## Random BN Generation

Random BN generation is possible via `bn_generator.py` script. The script generates a list of variable nodes and corresponding boolean functions, and stores them in a `.json` file.

Usage:

```sh
python bn_generator.py -s 42 -c 100 -ds-path datasets/boolean_networks.json
```

Trajectory generation from the BNs is available via `trajectory_generator.py`. The script generates a dictionary that for each of the boolean networks holds its' ID in the source dataset and a list of trajectories, where each of them is an object with parameters such as:
- synchronous: `True` or `False` 
- length: `int`
- frequency: `int`
- states: `lst[str]`

The script requires a range of frequencies and trajectory lengths to have the data sampled from. The next arguments are the number of synchronous trajectories sampled and asynchronous trajectories sampled. Defaultly, there's many more async trajectories than synchronous, as the synchronous are much more predictable.

Alongside the regular trajectory data within a .json file, the script also saves them onto a bnf-digestive text format. There, for each boolean network, all sets of trajectories are concatenated and saved inside the .txt file.

Usage:
```sh
python trajectory_generator.py \
    -fr-lo 1 \
    -fr-hi 5 \
    -len-lo 10 \
    -len-hi 500 \
    -sync-no 100 \
    -async-no 100 \
    -bn-ds datasets/boolean_networks.json \
    -tg-ds datasets/trajectory_samples.json \
    -tg-ds-txt datasets/testcase_0 \
    -lf logs/traj_gen.log \
    -s 42
```

The ```perform_tests.sh``` script is used for performing various number of test configurations, e.g. for a generated set of boolean networks using ```bn_generator.py```, basing on a set of configs present in ```perform_tests.sh``` code, the script generates a set of trajectories, saves them and performs a trajectory inference using ```trajectory_inference.sh``` file. 

IMPORTANT NOTE - In order for the scripts to work, BNF has to be installed using [these instructions](https://bioputer.mimuw.edu.pl/software/bnf/bnfinder_manual.pdf)

Regarding directories:

```datasets``` is used for containing data for the experiments - files such as ```boolean_networks.json```, ```*_trajectory_samples.json```, ```*_bn_*_trajectories.txt```

```inference``` is used for containing the results of BNF inference with .sif files for each of the tests.

```logs``` contains all the logs collected during boolean networks generation and trajectories generations.
