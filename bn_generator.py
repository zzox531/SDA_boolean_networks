import networkx as nx
import boolean as bool
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
import logging
import os

from boolean_network import BN

os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    filename="logs/gen.log",
    filemode="w",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def set_seed(seed: int):
    np.random.seed(seed)

def generate_functions(
    variables: list[str]
) -> list[str]:
    """
    This function uniformly generates a random combination of functions for each of the variables.
    Each of the functions has between 1 to 3 variables influencing the result variable

    Args:
        variables (list[str]): list of variables as strings

    Returns:
        list[str]: A list of strings representing the Boolean functions for the corresponding nodes
            e.g. '(x0 & ~x1) | x2', where 'x0', 'x1', and 'x2' are node names.
    """
    funs = []
    for child in variables:
        # Generate parent list
        size = np.random.randint(1, 4)
        possible_parents = variables[:]
        possible_parents.remove(child)
        parents = []
        for _ in range(size):
            par = str(np.random.choice(possible_parents))
            parents.append(par)
            possible_parents.remove(par)
        
        # Generate value table for a function.
        values = [np.random.randint(0, 2) for _ in range(2 ** size)]

        # Generate equal clause using DNF form
        # For each row with value = True we generate a clause (var1 & var2 & var3)
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
        funs.append(" | ".join(clause_parts) if len(clause_parts) > 0 else ("FALSE"))
        logging.info(f"Function for {child} with parents {parents} has values {values}. Function clause is {funs[-1]}.")
    return funs

          

def generate_bn(
    size: int
) -> BN:
    """
    This function generates a random boolean network of size n using generate_functions() within to generate a random combination of functions

    Args:
        size (int): Number of nodes in the returned Boolean Network 

    Returns:
        BN: Boolean Network class defined in boolean_network.py
    """
    
    nodes = [f"x{i}" for i in range(size)]
    
    functions = generate_functions(nodes)

    return BN(nodes, functions)

bn = generate_bn(5)