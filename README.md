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

Usage:
```sh
python trajectory_generator.py -fr-lo 1 -fr-hi 5 -len-lo 5 -len-hi 30 -sync-no 10 -async-no 100 -bn-ds datasets/boolean_networks.json -tg-ds datasets/trajectory_samples.json -s 42
```

Parameters:

- SEED - Set RNG seed for controlling output
- count - Number of BNs to generate
- ds_filename - Name of a `.json` file to store the BNs to.