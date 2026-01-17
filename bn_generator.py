import networkx as nx
import boolean as Bool
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
import numpy.random as r
import logging
import os
import json
import argparse
import glob

from boolean_network import BN

def set_seed(seed: int):
    r.seed(seed)

def load_bn_from_path(filepath: str) -> BN:
    """
    Loads a Boolean network from a JSON file path.
    
    Args:
        filepath (str): Path to the JSON file containing BN data
        
    Returns:
        BN: Boolean Network class defined in boolean_network.py
    """
    
    with open(filepath, 'r') as f:
        bn_data = json.load(f)
    
    nodes = bn_data["nodes"]
    functions = bn_data["functions"]
    
    # Convert attrs_async from list of strings to set of tuples
    attrs_async = set()
    for state_str in bn_data["attrs_async"]:
        state_tuple = tuple(map(int, state_str.strip("()").split(", ")))
        attrs_async.add(state_tuple)
    
    # Convert attrs_sync from list of strings to set of tuples
    attrs_sync = set()
    for state_str in bn_data["attrs_sync:"]:  # Note: typo in JSON has colon
        state_tuple = tuple(map(int, state_str.strip("()").split(", ")))
        attrs_sync.add(state_tuple)
    
    # Convert parents_async
    parents_async = {}
    for key_str, parent_list in bn_data["parents_async"].items():
        key_tuple = tuple(map(int, key_str.strip("()").split(", ")))
        parent_tuples = [tuple(map(int, parent_str.strip("()").split(", "))) for parent_str in parent_list]
        parents_async[key_tuple] = parent_tuples
    
    # Convert parents_sync
    parents_sync = {}
    for key_str, parent_list in bn_data["parents_sync"].items():
        key_tuple = tuple(map(int, key_str.strip("()").split(", ")))
        parent_tuples = [tuple(map(int, parent_str.strip("()").split(", "))) for parent_str in parent_list]
        parents_sync[key_tuple] = parent_tuples
    
    return BN(nodes, functions, attrs_async, attrs_sync, parents_async, parents_sync)

def get_bn_paths(filename_prefix: str) -> list[str]:
    """
    Get all file paths matching the Boolean Network filename pattern.
    
    Args:
        filename_prefix (str): Prefix for the BN files (e.g., "datasets/bn_")
    
    Returns:
        list[str]: Sorted list of file paths matching the pattern
    """
    pattern = f"{filename_prefix}*.json"
    files = sorted(glob.glob(pattern))
    
    if not files:
        return []
    
    return files

def generate_functions(
    variables: list[str]
) -> list[str]:
    """
    This function uniformly generates a random combination of functions for each of the variables.
    Each of the functions has between 1 to 3 parent variables.
    Generation is done using value table and DNF form for generating equal clause.

    Args:
        variables (list[str]): list of variables as strings

    Returns:
        list[str]: A list of strings representing the Boolean functions for the corresponding nodes
            e.g. '(x0 & ~x1) | x2', where 'x0', 'x1', and 'x2' are node names.
    """
    funs = []
    for child in variables:
        # Generate parent list
        size = r.randint(1, 3)
        possible_parents = [v for v in variables if v != child]
        parents = r.choice(possible_parents, size, replace=False)
        
        # Generate value table for a function.
        values = [r.randint(0, 2) for _ in range(2 ** size)]

        # Generate equal clause using DNF form
        clause_parts = []
        for i, val in enumerate(values):
            if val == 1:
                vars = []
                for e in range(size):
                    # Iterator e is used as a bit mask for current variable assignment.
                    if i & 2 ** e:
                        vars.append(parents[e])
                    else:
                        vars.append("~" + parents[e])
                clause_parts.append("(" + " & ".join(vars) + ")")
        if len(clause_parts) > 0:
            funs.append(" | ".join(clause_parts))
        else:
            funs.append("(" + ") & (".join(parents) + ") & FALSE")
        logging.info(f"Function for {child} with parents {parents} has values {values}. Function clause is {funs[-1]}.")
    return funs

          

def generate_bn(
    size: int,
    visuals: bool,
    visual_dir: str,
    id: int
) -> tuple[list[str], list[str]]:
    """
    This function generates a random boolean network of size n using generate_functions() within to generate a random combination of functions

    Args:
        size (int): Number of nodes in the returned Boolean Network 

    Returns:
        BN: Boolean Network class defined in boolean_network.py
    """
    
    nodes = [f"x{i}" for i in range(size)]
    
    functions = generate_functions(nodes)

    bn = BN(nodes, functions)
    if visuals:
        os.makedirs(os.path.dirname(visual_dir), exist_ok=True)
        if bn.num_nodes < 6:
            bn.draw_state_transition_system(f"{visual_dir}BN{id}.png")

    parents_async_serializable = {str(k): [str(v) for v in val] for k, val in bn.parents_async.items()}
    parents_sync_serializable = {str(k): [str(v) for v in val] for k, val in bn.parents_sync.items()}
    
    res = {
        "nodes": nodes,
        "functions": functions,
        "attrs_async": [str(state) for state in bn.attractor_set_async],
        "attrs_sync:": [str(state) for state in bn.attractor_set_sync],
        "parents_async": parents_async_serializable,
        "parents_sync": parents_sync_serializable
    }
    
    return res

def generate_ds(
        count: int,
        filename_prefix: str,
        visuals: bool,
        visual_dir: str
):
    """
    This function generates batch of boolean networks of random sizes and stores the result in a .json file for further use.

    Args:
        count (int): Number of BNs to generate
        filename (str): Name file for the dataset to be generated.
    """
    os.makedirs(os.path.dirname(filename_prefix), exist_ok=True)
    
    for i in range(count):
        size = r.randint(2, 3)
        bn = generate_bn(size, visuals, visual_dir, i)
        # Write to file bn_<i>.json
        with open(filename_prefix + f"{i}.json", "w") as f:
            json.dump(bn, f, indent=2)
    
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--count", type=int, default=5, help="Number of generated boolean networks")
    parser.add_argument("-d", "--ds-path", type=str, default="datasets/bn_", help="Dataset filename prefix (.json format)")
    parser.add_argument("-s", "--seed", type=int, default=42, help="RNG seed")
    parser.add_argument("--draw", action=argparse.BooleanOptionalAction, help="Generate visual representation of BNs")
    parser.add_argument("--draw-path", type=str, default="visual/", help="Directory for visual representation of BNs")

    args = parser.parse_args()
    set_seed(args.seed)

    # Set up logging
    os.makedirs("logs", exist_ok=True)
    logging.basicConfig(
        filename="logs/bn_gen.log",
        filemode="w",
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )

    generate_ds(args.count, args.ds_path, args.draw, args.draw_path)

if __name__ == "__main__":
    main()