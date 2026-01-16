# SDA 2 - Final Project - Report

## Authors: Ignacy Kozakiewicz, Jakub Misiaszek, Joanna Mali, Piotr Maksymiuk

This is the report of the final project for Statistical Data Analysis 2 course (2025/26).
The task was to investigate how the type and amount of data describing network dynamics influence the accuracy 
of inferring network structure within the framework of Bayesian networks.

The first part of the project focuses on constructing various Boolean networks, simu-
lating them under asynchronous and synchronous update modes to generate data, using
the [BNFinder2](https://bioputer.mimuw.edu.pl/software/bnf/) software tool  to build dy-
namic Bayesian networks from the simulated data, and finally assessing the quality of the
reconstructed network structures.

In the second part of the project, the insights gained from the first part were be applied
to reconstruct the structure of a network model representing a real-life biological process.

Regarding the code used for performing the analysis, it is all published in a github repository 
under [this](https://github.com/zzox531/SDA_boolean_networks) link.

# Prerequisites

This project uses [`uv`](https://github.com/astral-sh/uv) for environment management and package installation.

To install all dependencies:
```bash
uv sync
```

To run a Python script within this environment:
```bash
uv run <script_name.py> [arguments]
```
# Part I

## Subtask 1.

The first task of the project was to construct several Boolean Networks
with sizes ranging from 5 to 16 nodes, where each node would have no more
than 3 parent nodes and the functions governing individual nodes should
be generated at random.

This functionality is provided by the ```bn_generator.py``` script. It's example usage is:

```sh
uv run bn_generator.py -s 2137 -c 5 -d datasets/boolean_networks.json --draw --draw-path ./visual
```

Arguments to be passed to the ```bn_generator.py``` are:

- `-s`/`--seed`: `(int)` -  a random seed to be set within the generator, such that the execution of the code is replicable
- `-c`/`--count`: `(int)` - number of boolean networks to be generated
- `-d`/`--ds-path`: `(str)` - dataset filename path - a relative path leading to a `.json` file where the boolean networks are saved
- `--draw` - An option whether to generate visual representation of BNs. If set, saves the visuals for networks of size = 5 (higher numbers might be unreadable).
- `--draw-path`: `(str)`- A relative directory where the visual representations will be saved if `--draw` is set.

For each BN to be generated, the script samples a random number from 5 to 16 to be the number of nodes for the network. 

The variables names are set from `x0` up to `x15`.

After that, for each of the nodes $x_i$ and corresponding functions $f_i$ of the BN, the script:
- Generates a number $n_i$ of parent nodes of $x_i$
- Samples a set of parents $S_i$ of size $n_i$ from all the nodes using ```numpy.random.choice()``` (let's number variables within the set as $\{x_{1,S_i}, x_{2,S_i}, ... \}$)
- Generates $2^{n_i}$ numbers between 0 and 1 and saves them inside a list. (Let's call $J$ a set of such numbers $0 \leq j \leq 2^{n_i} - 1 $, that on index $j$, number $1$ was generated)

    If a number at index $j$ is equal to 1, then the clause $c_j$ corresponding to this index is added to the whole function via a logic `OR` operation.

    Clause correspondence is as following:

    We take a binary representation of the number $j$ to create a clause $c$. If the bit is lit on position $k$, then clause contains value $x_{k,S_i}$. If the bit is not lit, the clause contains value $\neg x_{k,S_i}$. The values are then ```AND```'ed within the clause. For example - $n_i = 3, S_i = \{x_0, x_2, x_4\}, j = 5 = 101_2$. Clause $c_j = (x_0 \wedge \neg x_2 \wedge x_4)$. 

    The entire clause $C = c_{j_1} \vee c_{j_2} \vee ... \vee c_{j_m}$, where $j_0, j_1, ..., j_m \in J$, $m = |J|$.

    We had to take under consideration such a case, where $|J| = 0$, then we simply take a logical $AND$ of all parents $x_{k,S_i}$ and logically and it with $0$ to make sure the value of the function stays as a ```FALSE```.

After generating all the functions, the data about the boolean network is stored inside ```--ds-path``` directory in a json format.

An example of such a file format is:

```json
[
  [
    [
      "x0",
      "x1",
      "x2",
      "x3",
      "x4"
    ],
    [
      "(~x4 & ~x1 & ~x3) | (x4 & x1 & ~x3) | (~x4 & ~x1 & x3) | (x4 & ~x1 & x3) | (~x4 & x1 & x3) | (x4 & x1 & x3)",
      "(~x2) | (x2)",
      "(x1 & ~x3 & ~x4) | (~x1 & x3 & ~x4) | (x1 & x3 & ~x4) | (x1 & ~x3 & x4) | (~x1 & x3 & x4)",
      "(~x0)",
      "(~x3 & ~x0 & ~x1)"
    ]
  ],
  [
    [
      "x0",
      "x1",
      "x2",
      "x3",
      "x4"
    ],
    [
      "(~x0)",
      "(~x2) | (x2)",
      "(~x4 & ~x1 & ~x3) | (x4 & x1 & ~x3) | (~x4 & ~x1 & x3) | (x4 & ~x1 & x3) | (~x4 & x1 & x3) | (x4 & x1 & x3)",
      "(x1 & ~-x3 & ~x4) | (~x1 & x3 & ~x4) | (x1 & x3 & ~x4) | (x1 & ~x3 & x4) | (~x1 & x3 & x4)",
      "(~x3 & ~x0 & ~x1)"
    ]
  ]
]
```

## Subtask 2.

Second subtask was to simulate trajectories of the generated networks in both synchronous and asynchronous modes to create datasets. This functionality is provided by the ```trajectory_generator.py``` python script. Its' example usage is: 

```sh
uv run trajectory_generator.py \
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

Arguments to be passed to the trajectory_generator.py are:


- ```-fr-lo``` / ```--frequency-low```: (int) – Lower bound for the frequency used during trajectory generation.

- ```-fr-hi``` / ```--frequency-high```: (int) – Upper bound for the frequency used during trajectory generation.

- ```-len-lo``` / ```--trajectory-length-low```: (int) – Minimum length of each generated trajectory.

- ```-len-hi``` / ```--trajectory-length-high```: (int) – Maximum length of each generated trajectory.

- ```-sync-no``` / ```--synchronous-number```: (int) – Number of synchronous trajectories to generate per Boolean network.

- ```-async-no``` / ```--asynchronous-number```: (int) – Number of asynchronous trajectories to generate per Boolean network.

- ```-bn-ds``` / ```--bn-ds-filename```: (str) – Dataset filename path to a .json file containing Boolean networks (generated by bn_generator.py).

- ```-tg-ds``` / ```--tg-ds-filename```: (str) – Output dataset filename path (.json) where generated trajectories will be saved.

- ```-tg-ds-txt``` / ```--tg-ds-txt```: (str) – Filename prefix for exporting generated trajectories into text-based BNF files.

- ```-lf``` / ```--log-file```: (str) – Path to a log file where execution logs will be stored.

- ```-s``` / ```--seed```: (int) – Random seed to ensure reproducible trajectory generation.

### General workflow

The script takes as input a dataset of Boolean Networks generated in Subtask 1 and, for each network, simulates a number of trajectories starting from random initial states. Each trajectory represents a sequence of Boolean states evolving according to the network’s update rules.

The trajectories are generated with:

- randomly sampled trajectory lengths
- randomly sampled sampling frequencies
- either synchronous or asynchronous update dynamics.

The resulting trajectories are stored in two formats:

- A structured .json dataset containing metadata and state sequences.
- A set of .txt files (one per Boolean Network) formatted for BNFinder2 inference tool.

### Trajectory generation

For each Boolean Network $\mathrm{BN}$, trajectories are generated using the ```generate_trajectory``` function. 

#### Initial state

- The initial state is sampled uniformly at random from $\{0,1\}^n$, where $n$ is the number of nodes in the network.

- Internally, states are represented as tuples of binary values and later converted to binary strings (e.g. ```"01011"```).

#### Update modes

Two update schemes are supported:

- Synchronous update

    All nodes are updated simultaneously.

    Given a state $s_t$, the next state is computed as:

    $s_{t+1} = f(s_t)$

    where each node’s update function is evaluated using the same current state.

- Asynchronous update

    At each step, a single successor state is chosen at random from the set of all possible asynchronous updates, i.e. states where exactly one node has been updated according to its Boolean function.

The update mode is determined per trajectory based on whether it belongs to the synchronous or asynchronous subset.

#### Frequency-based sampling

Each trajectory is generated step-by-step, but states are recorded only every $f$-th step, where:

$f \sim \mathcal{U}(\texttt{FrequencyLow}, \texttt{FrequencyHigh})$

Trajectory generation continues until the required number of recorded states reaches the randomly sampled trajectory length.

#### Trajectory dataset construction

The function ```generate_trajectory_ds``` iterates over all Boolean Networks and generates for each network:

- ```synchronous_number``` synchronous trajectories
- ```asynchronous_number``` asynchronous trajectories

For every generated trajectory, the following information is stored:

- update mode (synchronous: ```true``` / ```false```)
- sampling frequency
- trajectory length
- list of recorded states (as binary strings)

The output dataset is saved in JSON format as specified by ```--tg-ds-filename```. Each entry in the dataset has the structure:

```json
{
  "bn_id": 0,
  "trajectories": [
    {
      "synchronous": true,
      "frequency": 2,
      "length": 50,
      "states": ["0101", "1101", "1100", "..."]
    }
  ]
}
```

### Conversion to text-based format

After generating the JSON dataset, the script converts the trajectories into text files using the ```convert_trajectories_to_txt``` function.

For each Boolean Network:

- One ```.txt``` file is created.
- Columns correspond to individual time points of individual trajectories.
- Rows correspond to network variables ($x_0$, $x_1$, ..., $x_n$).
- Each cell contains a binary value (```0``` or ```1```) representing the state of a variable at a given time step.

The output format is compatible with BNFinder2 framework.

The filenames follow the pattern: "```<tg-ds-txt>```\_bn\_```<bn_id>```\_trajectories.txt"

### Reproducibility and logging

- A fixed random seed (```--seed```) ensures reproducibility of trajectory generation.
- Detailed execution logs are written to the specified log file (```--log-file```), including:
    
    - initial and final states of trajectories
    - trajectory lengths and frequencies
    - progress over Boolean Networks

## Subtask 3. 

The third subtask was to infer dynamic Bayesian Networks generated in substeps 1 and 2 using the BNFinder2 software tool. This functionality is provided by the ```trajectory_inference.sh``` bash script. 

The example usage for the script is: ```./trajectory_inferece.sh <output_prefix> <test_prefix> <scoring criterion: BDE | MDL>```

The script creates 3 subdirectories:
- ```./inference``` 
- ```./inference/sif```
- ```./inference/cpd```

The script finds all files within the ```./datasets``` subdirectory which match a regex: ```"${test_prefix}_bn_*_trajectories.txt"```

The files contain txt format of trajectories generated by the ```trajectory_generator.py``` script in substep 2.

The script takes out the id of the bn from the filename, e.g. for filename ```test_0_bn_5_trajectories.txt```, the id is ```5```.

The script infers the bayesian networks, saving its' output in 2 formats, saving the tests inside subdirectories created before. 

The whole pipeline of generating trajectories and infering the dynamic Bayesian Networks is provided by the ```perform_tests.sh``` bash script. This script executes the ```trajectory_inference.sh``` within its' logic.

This bash script is the main orchestration entry point for running a suite of inference experiments end-to-end. It automates the two core steps of the pipeline:

- Generate trajectory datasets by simulating the Boolean networks stored in ```datasets/boolean_networks.json```.

- Infer network structure from those trajectories using our inference wrapper (```trajectory_inference.sh```, which in turn calls BNFinder2).

The goal is to evaluate how the inferred Dynamic Bayesian Network structures depend on the type and amount of observed dynamics (synchronous vs asynchronous trajectories, and sample size).

#### Example usage

```sh
./run_all_tests.sh
```

This will create (if missing) the directories:

- datasets/ (trajectory outputs)
- logs/ (generator logs)
- inference/ (inference outputs)

and then execute the test for each config defined in the variable ```configs```.

Each experiment is specified as a single quoted line with the following fields:

```"fr_lo fr_hi len_lo len_hi sync_no async_no test_prefix seed criterion"```

These fields are parsed into variables and used to construct the generator command, inference command, and output paths. Since configs is a plain Bash array, the number of experiments is not fixed: the user can add any number of entries, remove entries, or adjust parameters to create new test regimes.

#### Meaning of each field

- ```fr_lo```, ```fr_hi```

    Lower/upper bound for the sampling frequency used when recording states from the simulated dynamics.

- ```len_lo```, ```len_hi```

    Lower/upper bound for the trajectory length. Each generated trajectory length is sampled within this range.

- ```sync_no```

    Number of synchronous-update trajectories generated per Boolean network.

- ```async_no```

    Number of asynchronous-update trajectories generated per Boolean network.

- ```test_prefix```

    Prefix used to namespace all artifacts of the run (datasets, logs, inference outputs). This should be unique per experiment to avoid overwriting results.

- ```seed```

    RNG seed used during trajectory generation to ensure reproducibility.

- ```criterion```

    Scoring criterion passed to BNFinder2 during inference (e.g., BDE / MDL).

### Per-experiment execution

1) Directory creation

    For each configuration, the script derives a set of paths:

    - ```tg_json="datasets/${test_prefix}_trajectory_samples.json"```: JSON dataset of all generated trajectories

    - ```log_file="logs/traj_gen_${test_prefix}.log"```: generator log

    - ```out_prefix="inference/${test_prefix}"```: output namespace for inference results (used by the inference wrapper)

2) Trajetory generation
    
    The script calls:
    ```sh
    python3 trajectory_generator.py \
        -fr-lo <fr_lo> -fr-hi <fr_hi> \
        -len-lo <len_lo> -len-hi <len_hi> \
        -sync-no <sync_no> -async-no <async_no> \
        -bn-ds datasets/boolean_networks.json \
        -tg-ds datasets/<test_prefix>_trajectory_samples.json \
        -tg-ds-txt datasets/<test_prefix> \
        -lf logs/traj_gen_<test_prefix>.log \
        -s <seed>
    ```

    This step produces the trajectories, as described before.

3) Inference (```trajectory_inference.sh```)

    After generating the trajectories, the script runs:

    ```sh
    ./trajectory_inference.sh "<test_prefix>" "<test_prefix>" "<criterion>"
    ```

The script uses ```set -e```, so it stops immediately if trajectory generation or inference fails. This prevents partial/invalid experiment outputs from being mixed with successful runs.