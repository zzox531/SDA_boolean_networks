import logging
import os
import json
import argparse
from boolean_network import BN


variables_path = "CHICKEN-SEX-DETERMINATION-REDUCED\metadata.json"
functions_path = "CHICKEN-SEX-DETERMINATION-REDUCED\model.bnet"


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
    print(variables)
    print(functions)
    return variables, functions

def generate_network(
        filename: str,
        visuals: bool,
        visual_dir: str, 
):
    """
    This function generates boolean network object from a chosen chicken model.
    
    Args:
        filename (str): Name file for the dataset to be generated.
    """
    vars, funcs = read_network()
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w") as f:
        json.dump([vars, funcs], f, indent=2)
    
    if visuals:
        network = BN(vars, funcs)
        os.makedirs(os.path.dirname(visual_dir), exist_ok=True)
        network.draw_state_transition_system(f"{visual_dir}chickenBN.png")
        
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--ds-path", type=str, default="datasets/chicken_network.json", help="Dataset filename (.json format)")
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

