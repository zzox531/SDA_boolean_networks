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
                if p != k:
                    G.add_edge(p, k)

    logging.info(f"Inferred graph: {G}, with nodes {G.nodes} and with edges {G.edges}")
    # nx.draw(G)
    # plt.show()
    return G

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
    bn_paths = glob.glob(bn_files_prefix + "*.json")
    source_bns = {}
    for path in bn_paths:
        num = int(path[len(bn_files_prefix):-5])
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
    logging.info(f"Parsed inferred BNs DataFrame:\n{infer_bns.head()}")
    return infer_bns

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

def delta_con_similarity(G1, G2):
    """
    Calculates DeltaCon similarity for small graphs (dense matrices).
    Ideal for N <= 1000 nodes.
    """
    # 1. Align Nodes
    # Get all unique nodes from both graphs and sort them to ensure matching indices
    nodes = sorted(list(set(G1.nodes()) | set(G2.nodes())))
    n = len(nodes)
    
    # 2. Get Dense Adjacency Matrices
    # nodelist ensures row 0 corresponds to the same node in both matrices
    A1 = nx.to_numpy_array(G1, nodelist=nodes)
    A2 = nx.to_numpy_array(G2, nodelist=nodes)
    
    # 3. Create Degree Matrices (Diagonal)
    # Sum of rows gives the degree of each node
    D1 = np.diag(np.sum(A1, axis=1))
    D2 = np.diag(np.sum(A2, axis=1))
    
    # 4. Determine Epsilon (Weighting Factor)
    # 1 / (1 + max_degree across both graphs)
    max_d = max(D1.max(), D2.max())
    epsilon = 1 / (1 + max_d)
    
    # 5. Compute Affinity Matrices (S)
    # Formula: S = inverse(I + eps^2 * D - eps * A)
    I = np.eye(n)
    
    # Matrix 1
    M1 = I + (epsilon**2 * D1) - (epsilon * A1)
    S1 = np.linalg.inv(M1)
    
    # Matrix 2
    M2 = I + (epsilon**2 * D2) - (epsilon * A2)
    S2 = np.linalg.inv(M2)
    
    # 6. Calculate Matusita Distance
    # Sum of squared differences of square roots
    # Note: We take absolute value before sqrt to handle tiny negative floating point errors
    diff = np.sqrt(np.abs(S1)) - np.sqrt(np.abs(S2))
    matusita_dist = np.sqrt(np.sum(diff**2))
    
    # 7. Convert to Similarity (Inverse of Distance)
    # Result is between 0 (totally different) and 1 (identical)
    similarity = 1 / (1 + matusita_dist)
    
    return similarity

def draw_plot(source: dict[int, nx.DiGraph], inferred: pd.DataFrame, test_name: str, title: str, value: str):
    row_configs = [
        (True, True, "Sync BDE"),
        (True, False, "Sync MDL"),
        (False, True, "Async BDE"),
        (False, False, "Async MDL")
    ]

    # Create 4 rows x 2 columns grid
    fig, axes = plt.subplots(4, 2, figsize=(16, 20))
    fig.suptitle(f"{title}", fontsize=16)

    for row_idx, (is_sync, is_bde, label) in enumerate(row_configs):
        
        # Select the subplots for this row
        ax_spectral = axes[row_idx, 0]
        ax_deltacon = axes[row_idx, 1]
        
        # Set titles and labels
        ax_spectral.set_ylabel(f"{label}")
        
        if row_idx == 0:
            ax_spectral.set_title("Spectral Distance (Lower is better)")
            ax_deltacon.set_title("DeltaCon Similarity (Higher is better)")
        if row_idx == 3:
            ax_spectral.set_xlabel(f"{value}")
            ax_deltacon.set_xlabel(f"{value}")

        # For mean calculation
        spectral_sum = None
        deltacon_sum = None
        sorted_x = None

        # Plot all BNs
        num_bns = inferred['bn_number'].nunique()
        
        for bn_id in range(num_bns): 
            sliced = inferred[
                (inferred['bn_number'] == bn_id) & 
                (inferred['type'] == test_name) & 
                (inferred['bde'] == is_bde) &
                (inferred['sync'] == is_sync)
            ]
            
            sliced = sliced.sort_values(by='value', ascending=True)
            
            if sliced.empty:
                logging.warning(f"No data for BN {bn_id} with sync={is_sync} and bde={is_bde}")
                continue

            x_values = sliced['value'].tolist()
            y_spectral = []
            y_deltacon = []
            
            G_source = source[bn_id]
            
            logging.info(f"Processing BN {bn_id} for sync={is_sync}, bde={is_bde}, test={test_name}, values={x_values}")
            for i, G_inferred in enumerate(sliced['graph']):
                logging.info(f"Comparing source BN {bn_id} with inferred graph for value {x_values[i]}\nG1 structure: Nodes {G_source.nodes}, Edges {G_source.edges}\nG2 structure: Nodes {G_inferred.nodes}, Edges {G_inferred.edges}")
                spec = spectral_similarity(G_source, G_inferred)
                y_spectral.append(spec)
                
                dc = delta_con_similarity(G_source, G_inferred)
                y_deltacon.append(dc)
            
            # For mean calculation
            if spectral_sum is None:
                spectral_sum = np.array(y_spectral)
                deltacon_sum = np.array(y_deltacon)
                sorted_x = x_values
            else:
                spectral_sum += np.array(y_spectral)
                deltacon_sum += np.array(y_deltacon)

            # Plot lines
            ax_spectral.plot(x_values, y_spectral, marker='o', 
                             alpha=0.3, linewidth=1,  # Low opacity
                             label=f'BN {bn_id}')
            
            ax_deltacon.plot(x_values, y_deltacon, marker='o', # linestyle='--', 
                             alpha=0.3, linewidth=1,  # Low opacity
                             label=f'BN {bn_id}')

        # Calculate mean        
        mean_spectral = spectral_sum / num_bns
        mean_deltacon = deltacon_sum / num_bns
        
        # Plot Mean Spectral
        ax_spectral.plot(sorted_x, mean_spectral, 
                         color='black', linewidth=3, # Thick and distinct
                         label='Mean')
        
        # Plot Mean DeltaCon
        ax_deltacon.plot(sorted_x, mean_deltacon, 
                         color='black', linewidth=3, linestyle='--',
                         label='Mean')

    # Add legend (ensure 'Mean' is included)
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='lower center', ncol=6, bbox_to_anchor=(0.5, 0.01))

    plt.tight_layout()
    plt.subplots_adjust(bottom=0.10, top=0.93) 
    plt.show()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-bn-pref", "--bn-files-prefix", type=str, help="File path prefix to source BNs", default="datasets/bn_")
    parser.add_argument("-infer-dir", "--inference-dir", type=str, help="Directory name for inferenced DBNs", default="inference/cpd/")
    parser.add_argument("-t", "--test-name", type=str, help="Test name to filter BNs, all by default")
    args = parser.parse_args()

    os.makedirs("logs", exist_ok=True)
    logging.basicConfig(
        filename="logs/distance.log",
        filemode="w",
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )

    source = parse_all_source(f'{args.bn_files_prefix}')
    inferred = parse_all_infer(f'{args.inference_dir}')

    if args.test_name is None:
        for test in inferred['type'].unique():
            draw_plot(source, inferred, test, 'Distance Measures between Source and Inferred BNs', 'Compared value')
    else:
        draw_plot(source, inferred, args.test_name, 'Distance Measures between Source and Inferred BNs', 'Transient num to length ratio')

if __name__ == "__main__":
    main()