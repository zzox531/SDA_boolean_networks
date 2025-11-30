import networkx as nx
import boolean as bool
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import random

from boolean_network import BN

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
    
    # Size of the function expression
    size = random.choice([1, 2, 3])
    
    # Randomly chosen sample of variables
    chosen = random.sample(variables, size)
    
    chosen_negated = [('~' if random.getrandbits(1) else '') + v for v in chosen]
    
    if size == 1:
        expr = chosen_negated[0]
    elif size == 2:
        op = random.choice(['&', '|'])
        expr = f'({chosen_negated[0]} {op} {chosen_negated[1]})'
    else:
        # TODO - Uniformly generate functions that use all three variables and are unambiguous
        pass        

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