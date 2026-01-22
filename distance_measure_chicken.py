import networkx as nx
import numpy as np
import logging
import os
import argparse

from distance_measure import parse_source, parse_infer, spectral_distance, delta_con_similarity

def main():
    parser = argparse.ArgumentParser() 
    parser.add_argument("-s", "--source", type=str, help="Path to source BN (.json)", default="chicken_dataset/bn_0.json")
    parser.add_argument("-i", "--inferred", type=str, help="Path to inferred BN (.cpd)", default="chicken_inference/cpd/chicken_test-BDE-sync-0.cpd")
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
    spectral = spectral_distance(G_source, G_inferred)
    deltacon = delta_con_similarity(G_source, G_inferred)

    # Output results
    with open("chicken_inference/results.txt", "a") as f:
        f.write(f"Spectral Similarity: {spectral:.4f}\n")
        f.write(f"DeltaCon Similarity: {deltacon:.4f}\n")

if __name__ == "__main__":
    main()