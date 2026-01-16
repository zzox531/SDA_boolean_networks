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
from bn_generator import load_bn_from_path, get_bn_paths

class BN_params():
    """
    Class containing Boolean Network and it's additional parameters:

    Args:
        BN_struct (BN): A Boolean Network representation
        vars (list[str]): List of it's variables
        parents (list[list[str]]): Dictionary with all variable's parents
        MBs (list[list[str]]): Dictionary with all variable's Markov Blankets
    """

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
        self.MBs = MBs


def parse_source(
    source_path: str
) -> BN_params:
    """
    This function parses all Boolean Networks saved in source_path. The format
    allows for easy conversion to BN class.

    Args:
        source_path (str): Path to a file containting source BNs description
    
    Returns:
        BN_params: Identified BN with additional details
    """
    logging.info(f"Parsing BNs from file {source_path}")
    bn_struct = load_bn_from_path(source_path)
    
    print(bn_struct.node_names)
    print(bn_struct.functions_str)
    sort = sorted(list(zip(bn_struct.node_names, bn_struct.functions_str)), key=lambda x:x[0])
    vars, funs = map(list, zip(*sort))
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
        f"\tMarkov Blankets: {MBs}\n"
        f"Passing the BN to compare."
    )
    return BN_params(bn_struct, vars, parents, MBs)

def parse_infer(
        infer_path: str, 
        bn_id: int
    ) -> BN_params:
    """
    This function parses Dynamic Bayesian Networks inferred by BNFinder. It uses
    cpd format. It also computes additional details to make them similar to BN syntax.

    Args:
        infer_path (str): Name of a test case. The function looks up proper .cpd
            file by itself
        dbn_num (int): Number of expected networks. Necessary because all networks
            live in individual files.
    
    Returns:
        BN_params: inferred BN with additional details.
    """
    print(f"./inference/cpd/{infer_path}_{bn_id}.cpd")
    with open(f"./inference/cpd/{infer_path}_{bn_id}.cpd", 'r') as f:
        data = f.read()
        netw = eval(data)
        vars = list(netw.keys())
        parents = {v: netw[v]['pars'] for v in vars}
        children = {v: [w for w in vars if v in parents[w]] for v in vars}
        MBs = {v: list(
                set(itertools.chain(
                    parents[v], 
                    children[v], 
                    itertools.chain.from_iterable(parents[x] for x in children[v])
                )) - {v}
                )
            for v in vars}

        values = [
            [
                max(d, key=d.get) for k, d in netw[v]['cpds'].items() if k != None
            ] for v in vars
        ]
        assert(not any(None in v for v in values))

        # Inferred clause generation (from bn_generator)
        funs = []
        for v_num, v in enumerate(vars):
            size = len(parents[v])
            v_pars = parents[v][::-1]
            clause_parts = []
            for i, val in enumerate(values[v_num]):
                if val == 1:
                    clause_vars = []
                    for e in range(size):
                        # Iterator e is used as a bit mask for current variable assignment.
                        if i & 2 ** e:
                            clause_vars.append(v_pars[e])
                        else:
                            clause_vars.append("~" + v_pars[e])
                    clause_parts.append("(" + " & ".join(clause_vars) + ")")
            if len(parents[v]) == 0:
                funs.append("TRUE" if values[v_num][0] == 1 else "FALSE")
            elif len(clause_parts) > 0:
                funs.append(" | ".join(clause_parts))
            else:
                funs.append("(" + ") & (".join(v_pars) + ") & FALSE")
        
        infer_BN = BN(vars, funs, set(), set(), {}, {})
        logging.info(
            f"Received following BN:\n"
            f"\tVariables: {vars}\n"
            f"\tParents: {parents}\n"
            f"\tChildren: {children}\n"
            f"\tMarkov Blankets: {MBs}\n"
            f"\tMost probable values: {values}\n"
            f"\tInferred functions: {funs}\n"
            f"Passing the BN to compare."
        )
        return BN_params(infer_BN, vars, parents, MBs)

def measure_distance(bn_path: str, infer_path: str):
    source_bn_paths = get_bn_paths(bn_path)

    print(f'Comparing networks from test {infer_path}...')
    for path in source_bn_paths:
        bn_id = int(path.replace(bn_path, "").replace(".json", ""))
        print('\n==== TEST START ====\n\n')
        print(f'Network pair no. {bn_id}\n')

        s = parse_source(path)
        i = parse_infer(infer_path, bn_id)

        # Precision, Recall, F1 on parent sets.
        tp = 0
        fn = 0
        fp = 0
        for v in s.vars:
            par_s = set(s.parents[v])
            par_i = set(i.parents[v])
            tp += len(par_s & par_i)
            fp += len(par_i - par_s)
            fn += len(par_s - par_i)
        
        prec   = tp / (tp + fp)
        recall = tp / (tp + fn)
        f1     = (2 * prec * recall) / (prec + recall)
        print(
            f"Scores on parent sets: Precision = {prec}, "
            f"Recall = {recall}, F1 = {f1}\n"
        )

        # Precision, Recall, F1 on Markov Blankets
        tp = 0
        fn = 0
        fp = 0
        for v in s.vars:
            mb_s = set(s.MBs[v])
            mb_i = set(i.MBs[v])
            
            tp += len(mb_s & mb_i)
            fp += len(mb_i - mb_s)
            fn += len(mb_s - mb_i)

        prec   = tp / (tp + fp)
        recall = tp / (tp + fn)
        f1     = (2 * prec * recall) / (prec + recall)
        print(
            f"Scores on Markov Blankets: Precision = {prec}, "
            f"Recall = {recall}, F1 = {f1}\n"
        )

        # % of correct synchronous transitions
        state_size = len(s.vars)
        good_pairs = 0
        for cnt in range(2 ** state_size):
            state = []
            for var in range(state_size):
                if cnt & (2 ** var):
                    state.append(1)
                else:
                    state.append(0)
            
            s_n_state = s.BN_struct.get_neighbor_state_sync(state)
            i_n_state = i.BN_struct.get_neighbor_state_sync(state)
            good_pairs += (1 if s_n_state == i_n_state else 0)
        acc = good_pairs / (2 ** state_size)
        print(f"Accuracy of next state in synchronous mode = {acc}\n")

        # Precision, Recall, F1 on reachable states in async mode
        tp = 0
        fn = 0
        fp = 0
        state_size = len(s.vars)
        for cnt in range(2 ** state_size):
            state = []
            for var in range(state_size):
                if cnt & (2 ** var):
                    state.append(1)
                else:
                    state.append(0)

            async_n_s = s.BN_struct.get_neighbor_states_async(state)
            async_n_i = i.BN_struct.get_neighbor_states_async(state)
            tp += len(async_n_s & async_n_i)
            fp += len(async_n_i - async_n_s)
            fn += len(async_n_s - async_n_i)

        prec   = tp / (tp + fp)
        recall = tp / (tp + fn)
        f1     = (2 * prec * recall) / (prec + recall)
        print(
            f"Scores on asynchronous neighbor sets: Precision = {prec}, "
            f"Recall = {recall}, F1 = {f1}\n"
        )


        print('\n==== TEST END ====\n')



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-bn-pref", "--bn-files-prefix", type=str, required=True, help="File path prefix to source BNs")
    parser.add_argument("-i", "--inference", type=str, required=True, help="File name prefix to inferenced DBNs")

    args = parser.parse_args()

    os.makedirs("logs", exist_ok=True)
    logging.basicConfig(
        filename="logs/distance.log",
        filemode="w",
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )

    measure_distance(args.bn_files_prefix, args.inference)

if __name__ == "__main__":
    main()