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
import itertools

from boolean_network import BN

class BN_params():

    def __init__(
            self, 
            BN_struct: BN,
            vars: list,
            parents: dict,
            MBs: dict
        ):
        self.BN_struct = BN_struct
        self.vars = vars
        self.parents = parents
        self. MBs = MBs


def parse_source(source_path: str) -> list[BN_params]:
    logging.info(f"Parsing BNs from file {source_path}")
    with open(source_path, "r") as f:
        bns_data = json.load(f)
    
    BNs = []
    for vars, funs in bns_data:
        bn_struct = BN(vars, funs)
        parents = {v: list(set(re.findall("x[0-9]*", f))) for v, f in zip(vars, funs)}
        children = {v: [w for w in vars if v in parents[w]] for v in vars}
        MBs = {v: list(
                  set(itertools.chain(
                    parents[v], 
                    children[v], 
                    itertools.chain.from_iterable(parents[x] for x in children[v])
                  )) - {v}
                  )
              for v in vars}
        logging.info(
            f"Received following BN:\n"
            f"\tVariables: {vars}\n"
            f"\tParents: {parents}\n"
            f"\tChildren: {children}\n"
            f"\tMarkov Blankets{MBs}\n"
            f"Passing the BN to compare."
        )
        BNs.append(BN_params(bn_struct, vars, parents, MBs))
    return BNs

    
    

def measure_distance(source_path: str, inference_path: str):
    BNs = parse_source(source_path)
    print(BNs)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--source", type=str, required=True, help="File path to source Boolean Networks")
    parser.add_argument("-i", "--inference", type=str, required=True, help="File path prefix to inferenced DBNs")

    args = parser.parse_args()

    os.makedirs("logs", exist_ok=True)
    logging.basicConfig(
        filename="logs/distance.log",
        filemode="w",
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )

    measure_distance(args.source, args.inference)

if __name__ == "__main__":
    main()