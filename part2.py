import logging
import os
import json
import argparse
from boolean_network import BN
from pathlib import Path

# Join path components in an OS-independent way:
variables_path = Path("CHICKEN-SEX-DETERMINATION-REDUCED") / "metadata.json"
functions_path = Path("CHICKEN-SEX-DETERMINATION-REDUCED") / "model.bnet"

# variables_path = "CHICKEN-SEX-DETERMINATION-REDUCED/metadata.json"
# functions_path = "CHICKEN-SEX-DETERMINATION-REDUCED/model.bnet"


def read_network(): 
    variables = []
    inputs = []
    functions = []

    with open(variables_path, 'r') as file:
        data = json.load(file)
        variables += data["variable-names"]
        inputs += data["input-names"]
    
    with open(functions_path, 'r') as file:
        for line in file:
            _, fun = line.split(',', 1)
            fun = fun.strip()
            functions.append(fun)

    variables += inputs
    functions = functions[1:]
    functions.extend(inputs)
    return variables, functions

def generate_network(
        filename_prefix: str,
        visuals: bool,
        visual_dir: str, 
):
    """
    This function generates boolean network object from a chosen chicken model.
    
    Args:
        filename (str): Name file for the dataset to be generated.
    """
    vars, funcs = read_network()
    bn = BN(vars, funcs)
    
    parents_async_serializable = {str(k): [str(v) for v in val] for k, val in bn.parents_async.items()}
    parents_sync_serializable = {str(k): [str(v) for v in val] for k, val in bn.parents_sync.items()}
    
    res = {
        "nodes": vars,
        "functions": funcs,
        "attrs_async": [str(state) for state in bn.attractor_set_async],
        "attrs_sync:": [str(state) for state in bn.attractor_set_sync],
        "parents_async": parents_async_serializable,
        "parents_sync": parents_sync_serializable
    }
    os.makedirs(os.path.dirname(filename_prefix), exist_ok=True)
    with open(filename_prefix + '2137.json', "w") as f:
        json.dump(res, f, indent=2)
    
    if visuals:
        
        os.makedirs(os.path.dirname(visual_dir), exist_ok=True)
        if bn.num_nodes < 6:
            bn.draw_state_transition_system(f"{visual_dir}BN2137.png")
        
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--ds-path", type=str, default="datasets/bn_", help="Dataset filename prefix (.json format)")
    parser.add_argument("--draw", action=argparse.BooleanOptionalAction, help="Generate visual representation of BNs")
    parser.add_argument("--draw-path", type=str, default="visual/", help="Directory for visual representation of BNs")

    args = parser.parse_args()

    # Set up logging
    os.makedirs("logs", exist_ok=True)
    logging.basicConfig(
        filename="logs/bn_gen.log",
        filemode="w",
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )

    generate_network(args.ds_path, args.draw, args.draw_path)
    
    
    
if __name__ == "__main__":
    main()

