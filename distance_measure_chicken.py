import networkx as nx
import numpy as np
import logging
import os
import argparse
import re

from boolean_network import BN
from bn_generator import load_bn_from_path

def parse_source(source_path: str) -> nx.DiGraph:
    """Parse a single source Boolean Network."""
    logging.info(f"Parsing BN from file {source_path}")
    bn_struct = load_bn_from_path(source_path)
    G = nx.DiGraph()
    G.add_nodes_from(bn_struct.node_names)

    for i, f in enumerate(bn_struct.functions_str):
        parents = re.findall("x[0-9]*", f)
        for p in parents:
            G.add_edge(p, f"{bn_struct.node_names[i]}")

    logging.info(f"Graph: {G}, with nodes {G.nodes} and with edges {G.edges}")
    return G

def parse_infer(infer_path: str) -> nx.DiGraph:
    """Parse a single inferred BN from .cpd file."""
    logging.info(f"Loading inferred BN from {infer_path}")
    G = nx.DiGraph()
    with open(infer_path, 'r') as f:
        data = eval(f.read())
        
        for k, v in data.items():
            G.add_node(k)
            for p in v['pars']:
                if p != k:
                    G.add_edge(p, k)

    logging.info(f"Inferred graph: {G}, with nodes {G.nodes} and with edges {G.edges}")
    return G

def spectral_similarity(G: nx.DiGraph, H: nx.DiGraph) -> float:
    """Compute spectral similarity between two graphs."""
    eig_1 = nx.laplacian_spectrum(G)
    eig_1.sort()
    eig_2 = nx.laplacian_spectrum(H)
    eig_2.sort()

    spectral_distance = np.linalg.norm(eig_1 - eig_2)
    return 1 / (1 + spectral_distance)

def delta_con_similarity(G1: nx.DiGraph, G2: nx.DiGraph) -> float:
    """Calculate DeltaCon similarity between two graphs."""
    nodes = sorted(list(set(G1.nodes()) | set(G2.nodes())))
    n = len(nodes)
    
    A1 = nx.to_numpy_array(G1, nodelist=nodes)
    A2 = nx.to_numpy_array(G2, nodelist=nodes)
    
    D1 = np.diag(np.sum(A1, axis=1))
    D2 = np.diag(np.sum(A2, axis=1))
    
    max_d = max(D1.max(), D2.max())
    epsilon = 1 / (1 + max_d)
    
    I = np.eye(n)
    
    M1 = I + (epsilon**2 * D1) - (epsilon * A1)
    S1 = np.linalg.inv(M1)
    
    M2 = I + (epsilon**2 * D2) - (epsilon * A2)
    S2 = np.linalg.inv(M2)
    
    diff = np.sqrt(np.abs(S1)) - np.sqrt(np.abs(S2))
    matusita_dist = np.sqrt(np.sum(diff**2))
    
    return 1 / (1 + matusita_dist)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--source", type=str, required=True, help="Path to source BN (.json)")
    parser.add_argument("-i", "--inferred", type=str, required=True, help="Path to inferred BN (.cpd)")
    args = parser.parse_args()

    os.makedirs("logs", exist_ok=True)
    logging.basicConfig(
        filename="logs/distance.log",
        filemode="w",
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )

    # Parse networks
    G_source = parse_source(args.source)
    G_inferred = parse_infer(args.inferred)

    # Calculate similarities
    spectral = spectral_similarity(G_source, G_inferred)
    deltacon = delta_con_similarity(G_source, G_inferred)

    # Output results
    with open("chicken_inference/results.txt", "a") as f:
        f.write(f"Spectral Similarity: {spectral:.4f}\n")
        f.write(f"DeltaCon Similarity: {deltacon:.4f}\n")

if __name__ == "__main__":
    main()