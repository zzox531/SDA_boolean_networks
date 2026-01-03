import networkx as nx
import boolean as bool
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
import numpy.random as r
import logging
import os
import json
import argparse
from tqdm import tqdm

from boolean_network import BN

def set_seed(seed: int):
    r.seed(seed)
    
def generate_trajectory(
    bn: BN,
    frequency: int,
    length: int,
    synchronous: bool = True,
):
    """
    This function uniformly generates a trajectory for a given Boolean Network.
    It generates trajectories with a given frequency and attractor to tran ratio.

    Args:
        bn (BN): Boolean Network object
        frequency (int): Frequency of trajectory generation
        length (int): Length of the trajectory
        synchronous (bool, optional): Whether to use synchronous update. Defaults to True. False means asynchronous update.

    Returns:
        list[str]: A list of binary strings representing the state values in the trajectory
    """
    
    current_step = 1
    initial_state = tuple(r.randint(0, 2) for _ in range(bn.num_nodes))
    current_state = initial_state
    states = [initial_state]
    res = [bn.state_to_binary_str(initial_state)]
    
    while(len(states) < length):
        if synchronous:
            next_state = bn.get_neighbor_state_sync(current_state)
            current_state = next_state
        else:
            next_states = list(bn.get_neighbor_states_async(current_state))
            id = r.randint(0, len(next_states))
            current_state = next_states[id]

        if (current_step % frequency) == 0:
            res.append(bn.state_to_binary_str(current_state))
            states.append(current_state)
        
        current_step += 1
        
    logging.info(f"BN with generated trajectory of length {length} with frequency {frequency}. Initial state: {bn.state_to_binary_str(initial_state)}. Final state: {bn.state_to_binary_str(current_state)}.")
    
    return res
    
def generate_trajectory_ds(
    bn_list: list[BN],
    args: argparse.Namespace
):
    """
    This function generates a trajectory dataset for a list of Boolean Networks.

    Args:
        bn_list (list[BN]): List of Boolean Network objects
        args (argparse.Namespace): Command line arguments
    Returns:
        dict: A dictionary containing the trajectory dataset
    """
    
    bn_data = []
    
    for i, bn in enumerate(tqdm(bn_list, desc=f"Generating Trajectories for {len(bn_list)} Boolean Networks", unit="BN")):
        logging.info(f"Generating trajectories for BN {i+1}/{len(bn_list)} with {len(bn.node_names)} nodes.")
                
        trajectories = []
        for traj_no in range(args.synchronous_number + args.asynchronous_number):
            sync = traj_no < args.synchronous_number
            frequency = r.randint(args.frequency_low, args.frequency_high + 1)
            traj_len = r.randint(args.trajectory_length_low, args.trajectory_length_high + 1)
            traj = generate_trajectory(
                bn,
                frequency,
                traj_len,
                synchronous=sync
            )
            
            trajectories.append({
                "synchronous": sync,
                "frequency": frequency,
                "length": traj_len,
                "states": traj
            })
        
        bn_data.append({
            "bn_id": i,
            "trajectories": trajectories
        })
        
    os.makedirs(os.path.dirname(args.tg_ds_filename), exist_ok=True)
        
    with open(args.tg_ds_filename, "w") as f:
        json.dump(bn_data, f, indent=2)
        
def convert_trajectories_to_txt(args):
    """
    Convert trajectory samples from JSON to txt files for boolean network inference.
    Creates one .txt file per boolean network.
    """
    
    # Read the JSON data
    with open(args.tg_ds_filename, 'r') as f:
        data = json.load(f)
    
    # Process each boolean network
    for bn_data in data:
        bn_id = bn_data['bn_id']
        trajectories = bn_data['trajectories']
        
        # Determine number of variables from the first state
        if trajectories and trajectories[0]['states']:
            num_variables = len(trajectories[0]['states'][0])
        else:
            continue
        
        # Create variable labels (x0, x1, x2, ...)
        variable_labels = [f"x{i}" for i in range(num_variables)]
        
        # Generate column headers
        headers = []
        for traj_idx, trajectory in enumerate(trajectories):
            for time_step in range(len(trajectory['states'])):
                headers.append(f"serie{traj_idx}:{time_step}")
        
        # Create the data matrix
        data_matrix = []
        for var_idx in range(num_variables):
            row = []
            for traj_idx, trajectory in enumerate(trajectories):
                for state in trajectory['states']:
                    # Extract the bit for this variable from the state string
                    bit_value = state[var_idx]
                    row.append(bit_value)
            data_matrix.append(row)
        
        # Write to file
        output_filename = f"{args.tg_ds_txt}_bn_{bn_id}_trajectories.txt"
        
        with open(output_filename, 'w') as f:
            # Write header
            f.write('\t' + '\t'.join(headers) + '\n')
            
            # Write data rows
            for var_idx, row in enumerate(data_matrix):
                variable_label = variable_labels[var_idx]
                f.write(variable_label + '\t' + '\t'.join(row) + '\n')
        
        print(f"Created {output_filename} with {num_variables} variables and {len(headers)} time points")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-fr-lo", "--frequency-low", type=int, default=1, help="Lower bound for the frequency of trajectory generation")
    parser.add_argument("-fr-hi", "--frequency-high", type=int, default=1, help="Upper bound for the frequency of trajectory generation")
    parser.add_argument("-len-lo", "--trajectory-length-low", type=int, default=10, help="Minimum length of each generated trajectory")
    parser.add_argument("-len-hi", "--trajectory-length-high", type=int, default=500, help="Maximum length of each generated trajectory")
    parser.add_argument("-sync-no", "--synchronous-number", type=int, default=100, help="Number of synchronous trajectories to generate per Boolean network")
    parser.add_argument("-async-no", "--asynchronous-number", type=int, default=0, help="Number of asynchronous trajectories to generate per Boolean network")
    parser.add_argument("-bn-ds", "--bn-ds-filename", type=str, default="datasets/boolean_networks.json", help="Dataset filename of boolean networks (.json format, generated by bn_generator.py)")
    parser.add_argument("-tg-ds", "--tg-ds-filename", type=str, default="datasets/trajectory_samples.json", help="Trajectory dataset filename (.json format, to be generated)")
    parser.add_argument("-tg-ds-txt", "--tg-ds-txt", type=str, default="datasets/testcase_0", help="Trajectory dataset filename prefix for txt bnf files")
    parser.add_argument("-lf", "--log-file", type=str, default="logs/traj_gen.log", help="Filename to put the logs in")
    parser.add_argument("-s", "--seed", type=int, default=42, help="RNG seed")
    

    args = parser.parse_args()
    set_seed(args.seed)

    # Set up logging
    os.makedirs("logs", exist_ok=True)
    logging.basicConfig(
        filename=args.log_file,
        filemode="w",
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )
    
    with open(args.bn_ds_filename, "r") as f:
        bn_data = json.load(f)
    bns = [BN(nodes, functions) for nodes, functions in bn_data]
    
    generate_trajectory_ds(bns, args)
    
    convert_trajectories_to_txt(args)

if __name__ == "__main__":
    main()
    