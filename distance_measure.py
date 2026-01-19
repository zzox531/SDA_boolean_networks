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
import re
from tqdm import tqdm
import pandas as pd
import glob

from boolean_network import BN
from bn_generator import load_bn_from_path, get_bn_paths

def parse_source(
    source_path: str
) -> nx.DiGraph:
    """
    This function parses all Boolean Networks saved in source_path. The format
    allows for easy conversion to BN class.

    Args:
        source_path (str): Path to a file containting source BNs description
    
    Returns:
        nx.DiGraph: Parsed BN in networkx DiGraph format
    """
    logging.info(f"Parsing BNs from file {source_path}")
    bn_struct = load_bn_from_path(source_path)
    G = nx.DiGraph()

    G.add_nodes_from(bn_struct.node_names)

    for i, f in enumerate(bn_struct.functions_str):
        parents = re.findall("x[0-9]*", f)
        for p in parents:
            G.add_edge(p, f"{bn_struct.node_names[i]}")

    logging.info(f"Graph: {G}, with nodes {G.nodes} and with edges {G.edges}")
    # nx.draw(G)
    # plt.show()
    return G

def parse_infer(
        infer_path: str,
    ) -> nx.DiGraph:
    """
    This function parses Dynamic Bayesian Networks inferred by BNFinder. It uses
    cpd format.

    Args:
        infer_path (str): Name of a test case. The function looks up proper .cpd
            file by itself
    
    Returns:
        nx.DiGraph: inferred BN in networkx DiGraph format.
    """
    logging.info(f"Loading inferred BN from {infer_path}")
    G = nx.DiGraph()
    with open(f"{infer_path}", 'r') as f:
        data = eval(f.read())
        
        for k, v in data.items():
            # logging.info(f"Variable {k} with data {v}")
            G.add_node(k)
            for p in v['pars']:
                G.add_edge(p, k)

    logging.info(f"Inferred graph: {G}, with nodes {G.nodes} and with edges {G.edges}")
    # nx.draw(G)
    # plt.show()
    return G

def spectral_similarity(G: nx.DiGraph, H: nx.DiGraph):
    # Compute eigenvalues and sort them
    eig_1 = nx.laplacian_spectrum(G)
    eig_1.sort()
    eig_2 = nx.laplacian_spectrum(H)
    eig_2.sort()

    # Compute spectral distance
    spectral_distance = np.linalg.norm(eig_1 - eig_2)
    logging.info(f'Spectral distance: {spectral_distance}\nSpectral similarity: {1 / (1 + spectral_distance)}')
    return 1 / (1 + spectral_distance)

def parse_all_source(
    bn_files_prefix: str
) -> dict[int, nx.DiGraph]:
    """
    This function parses all source BNs from given prefix.
    Args:
        bn_files_prefix (str): File path prefix to source BNs

    Returns:
        dict[int, nx.DiGraph]: Dictionary of parsed source BNs
    """
    bn_paths = get_bn_paths(bn_files_prefix)
    source_bns = {}
    for num, path in enumerate(bn_paths):
        source_bns[num] = parse_source(path)
    return source_bns

def parse_all_infer(
    infer_dir: str
) -> pd.DataFrame:
    """
    This function parses all BNs inferred from given directory.
    Args:
        infer_dir (str): Directory name for inferred BNs

    Returns:
        pd.DataFrame: DataFrame containing parsed inferred BNs
    """
    infer_paths = glob.glob(os.path.join(infer_dir, "*.cpd"))
    # infer_bns = pd.DataFrame(columns=['type', 'value', 'sync', 'criterion', 'bn_number', 'graph'])
    rows = []
    pbar = tqdm(infer_paths, desc="Parsing inferred BNs")
    for path in pbar:
        name = os.path.basename(path)
        name = os.path.splitext(name)[0]
        logging.info(f"Parsing inferred BN: {name}")
        args = name.split('-')
        rows.append({
            'type': str(args[0]),
            'value': float(args[1]),
            'sync': args[2] == 'sync',
            'bde': args[3] == 'BDE',
            'bn_number': int(args[4]),
            'graph': parse_infer(path)
        })
    infer_bns = pd.DataFrame(rows)
    logging.info(f"Parsed inferred BNs DataFrame:\n{infer_bns.info()}\n{infer_bns.head()}")
    return infer_bns

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-bn-pref", "--bn-files-prefix", type=str, help="File path prefix to source BNs", default="datasets/bn_")
    parser.add_argument("-infer-dir", "--inference-dir", type=str, help="Directory name for inferenced DBNs", default="inference/cpd/")

    args = parser.parse_args()

    os.makedirs("logs", exist_ok=True)
    logging.basicConfig(
        filename="logs/distance.log",
        filemode="w",
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )

    source = parse_all_source('datasets/bn_')
    inferred = parse_all_infer('inference/cpd/')

    sliced = inferred[
        (inferred['bn_number'] == 0) & 
        (inferred['type'] == 'ratio') & 
        (inferred['bde'] == False) &
        (inferred['sync'] == False)
    ]
    sliced = sliced.sort_values(by='value', ascending=False)
    print(sliced.head())
    for v, g in zip(sliced['value'], sliced['graph']):
       print(v, spectral_similarity(source[0], g))

    # measure_distance_spectral(source, inferred)
    # measure_distance(source, inferred)

if __name__ == "__main__":
    main()