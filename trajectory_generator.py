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
import random

from boolean_network import BN
from bn_generator import load_bn_from_path, get_bn_paths

def set_seed(seed: int):
    r.seed(seed)
    
def get_next_state(
    bn: BN,
    state: tuple[int, ...],
    synchronous: bool = True
) -> tuple[int, ...]:
    """
    This function generates next state for a given state and a Boolean Network.

    Args:
        bn (BN): Boolean Network object
        state (tuple[int, ...]): Current state we compute the function of
        synchronous (bool, optional): 
            Wether we move via a synchronous or asynchronous transition
            
    Returns: 
        tuple[int, ...]: A tuple representing the next state after the transition in the BN.
    """

    if synchronous:
        next_state = bn.get_neighbor_state_sync(state)
        return next_state
    else:
        next_states = list(bn.get_neighbor_states_async(state))
        return random.choice(next_states)

def get_parent_state(
    bn: BN,
    state: tuple[int, ...],
    synchronous: bool = True
) -> tuple[int, ...]:
    """
    This function generates a previous state for a given state and a Boolean Network.
    It checks all the parent states of a specific state and uniformly samples a parent
    out of the set. If there is no parent of a specific state, then None is returned

    Args:
        bn (BN): Boolean Network object
        state (tuple[int, ...]): Current state of which we compute the parent
        snychronous (bool, optional):
            Wether we search for a parent in a synchronous or asynchronous way

    Returns:
        tuple[int, ...]: A tuple representing the parent state, if no found returns None
    """
    
    if synchronous:
        return bn.sample_parent_state_async(state)
    else:
        return bn.sample_parent_state_async(state)

def generate_trajectory(
    bn: BN,
    frequency: int,
    length: int,
    trans_attr_ratio: float,
    synchronous: bool = True
) -> tuple[list[str], float]:
    """
    This function uniformly generates a trajectory for a given Boolean Network.
    It generates trajectories with a given frequency and attractor to tran ratio.

    Args:
        bn (BN): Boolean Network object
        frequency (int): Frequency of trajectory generation
        length (int): Length of the trajectory
        synchronous (bool, optional): Whether to use synchronous update. Defaults to True. False means asynchronous update.

    Returns:
        tuple[list[str], float]: 
            A list of binary strings representing the state values in 
            the trajectory and best transient/attr ratio achieved for the sample
    """
    # print("Generatin...")
    
    current_step = 0
    initial_state = tuple(r.randint(0, 2) for _ in range(bn.num_nodes))
    current_state = initial_state
    
    res = [bn.state_to_binary_str(initial_state)]
    in_attractor = False
    
    # In order to change the transient/attractor ratio,
    # we need to be sure that we've reached an attractor state,
    # thus (in_attractor == False) condition in the while loop
    while(len(res) < length or in_attractor == False):
        # print("State: ", current_state, synchronous)
        # print("attractors: ")
        # for state in bn.attractor_set_sync:
            # print(state)
        if bn.is_attractor(current_state, synchronous):
            in_attractor = True

        if (current_step % frequency) == 0:
            res.append(current_state)
            
        current_state = get_next_state(bn, current_state, synchronous)
        
        current_step += 1
        
    # Take last length element of the result
    res = res[len(res) - length:]
    
    # # print("Elo")
    
    # count number of transients & attractors
    transient_states = 0
    attractor_states = 0
    for el in res:
        if bn.is_attractor(el, synchronous):
            attractor_states += 1
        else:
            transient_states += 1
        
    # This part of code calculates the optimal ratio and 
    # checks wether we need to lengthen our attractor suffix
    # or transient prefix in order to reach the optimal ratio
    expected_transient_states = round(trans_attr_ratio * length)
    
    if (transient_states > expected_transient_states):
        while(transient_states > expected_transient_states):
            if (current_step % frequency) == 0:
                # As we've added an attractor state, then we reduce the number of 
                # transient states by 1
                res.append(current_state)
                transient_states -= 1
            
            current_state = get_next_state(bn, current_state, synchronous)
            
            current_step += 1
        
        # Take last length elements of the array
        res = res[len(res) - length:]
    elif (transient_states < expected_transient_states):
        # Reverse the array such that appending to it will 
        # increase the transient state prefix
        res = res[::-1]
        current_state = get_parent_state(bn, res[-1], synchronous)
        current_step = -1
        
        # We need additional condition on current_state != None, as we 
        # may have a case where a node has no parents
        while(transient_states < expected_transient_states and current_state != None):
            if (current_step % frequency) == 0:
                res.append(current_state)
                transient_states += 1
            
            current_state = get_parent_state(bn, current_state, synchronous)
            
            current_step -= 1
        
        # Reverse the array again and take first length elements as the result
        res = res[::-1]
        res = res[:length]
    
    logging.info(f"BN with generated trajectory of length {length} with frequency {frequency}. Initial state: {bn.state_to_binary_str(res[0])}. Final state: {bn.state_to_binary_str(res[length-1])}.")
    
    transient_states = 0
    for i in range(len(res)):
        if not bn.is_attractor(res[i], synchronous):
            transient_states += 1
        res[i] = bn.state_to_binary_str(res[i])
    
    # # print("Finished...")
    
    return res, transient_states / length
    
def generate_trajectory_ds(
    bn_paths: list[str],
    args: argparse.Namespace
):
    """
    This function generates a trajectory dataset for a list of Boolean Networks.

    Args:
        bn_paths (list[str]): List of file paths to Boolean Networks
        args (argparse.Namespace): Command line arguments
    Returns:
        dict: A dictionary containing the trajectory dataset
    """
        
    for i, path in enumerate(tqdm(bn_paths, desc=f"Generating Trajectories for {len(bn_paths)} Boolean Networks", unit="BN")):
        bn = load_bn_from_path(path)
        # Get BN number from the filepath suffix
        bn_id = int(path.replace(args.bn_ds_prefix, "").replace(".json", ""))
        
        logging.info(f"Generating trajectories for BN {i+1}/{len(bn_paths)} with {len(bn.node_names)} nodes.")
                
        trajectories = []
        for traj_no in range(args.synchronous_number + args.asynchronous_number):
            sync = traj_no < args.synchronous_number
            frequency = r.randint(args.frequency_low, args.frequency_high + 1)
            traj_len = r.randint(args.trajectory_length_low, args.trajectory_length_high + 1)
            target_ratio = r.uniform(args.trans_length_ratio_low, args.trans_length_ratio_high)
            traj, generated_ratio = generate_trajectory(
                bn,
                frequency,
                traj_len,
                target_ratio,
                synchronous=sync
            )
                        
            trajectories.append({
                "synchronous": sync,
                "frequency": frequency,
                "length": traj_len,
                "target_ratio": target_ratio,
                "generated_ratio": generated_ratio,
                "states": traj
            })
        
        os.makedirs(os.path.dirname(args.tg_ds_prefix), exist_ok=True)
            
        with open(args.tg_ds_prefix + f"{bn_id}.json", "w") as f:
            json.dump(trajectories, f, indent=2)
        
def convert_trajectories_to_txt(bn_paths, args):
    """
    Convert trajectory samples from JSON to txt files for boolean network inference.
    Creates one .txt file per boolean network.
    """
    
    # Read the JSON data
    for path in bn_paths:
        bn_id = int(path.replace(args.bn_ds_prefix, "").replace(".json", ""))
        
        with open(args.tg_ds_prefix + f"{bn_id}.json", 'r') as f:        
            trajectories = json.load(f)
            
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
    parser.add_argument("-ratio-lo", "--trans-length-ratio-low", type=float, default=0.2, help="Lower bound for the transient to trajectory length ratio")
    parser.add_argument("-ratio-hi", "--trans-length-ratio-high", type=float, default=0.4, help="Upper bound for the transient to trajectory length ratio")
    parser.add_argument("-fr-lo", "--frequency-low", type=int, default=1, help="Lower bound for the frequency of trajectory generation")
    parser.add_argument("-fr-hi", "--frequency-high", type=int, default=1, help="Upper bound for the frequency of trajectory generation")
    parser.add_argument("-len-lo", "--trajectory-length-low", type=int, default=10, help="Minimum length of each generated trajectory")
    parser.add_argument("-len-hi", "--trajectory-length-high", type=int, default=500, help="Maximum length of each generated trajectory")
    parser.add_argument("-sync-no", "--synchronous-number", type=int, default=100, help="Number of synchronous trajectories to generate per Boolean network")
    parser.add_argument("-async-no", "--asynchronous-number", type=int, default=0, help="Number of asynchronous trajectories to generate per Boolean network")
    parser.add_argument("-bn-ds", "--bn-ds-prefix", type=str, default="datasets/bn_", help="Dataset filename prefix of boolean networks (.json format, generated by bn_generator.py)")
    parser.add_argument("-tg-ds", "--tg-ds-prefix", type=str, default="datasets/trajs_bn_", help="Trajectory dataset filename prefix for trajectories of a specific boolean network (.json format)")
    parser.add_argument("-tg-ds-txt", "--tg-ds-txt", type=str, default="datasets/test0", help="Trajectory dataset filename prefix for txt bnf files")
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
    
    print(args.bn_ds_prefix)
    
    bn_paths = get_bn_paths(args.bn_ds_prefix)
    
    print(bn_paths)

    generate_trajectory_ds(bn_paths, args)
    
    convert_trajectories_to_txt(bn_paths, args)

if __name__ == "__main__":
    main()
    