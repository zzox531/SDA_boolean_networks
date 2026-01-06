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
) -> list[BN_params]:
    """
    This function parses all Boolean Networks saved in source_path. The format
    allows for easy conversion to BN class.

    Args:
        source_path (str): Path to a file containting source BNs description
    
    Returns:
        list[BN_params]: List of identified BNs with additional details
    """
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
            f"\tMarkov Blankets: {MBs}\n"
            f"Passing the BN to compare."
        )
        BNs.append(BN_params(bn_struct, vars, parents, MBs))
    return BNs

def parse_infer(
        infer_path: str, 
        dbn_num: int
    ) -> list[BN_params]:
    """
    This function parses Dynamic Bayesian Networks inferred by BNFinder. It uses
    cpd format. It also computes additional details to make them similar to BN syntax.

    Args:
        infer_path (str): Name of a test case. The function looks up proper .cpd
            file by itself
        dbn_num (int): Number of expected networks. Necessary because all networks
            live in individual files.
    
    Returns:
        list[BN_params]: List of inferred BNs with additional details.
    """
    BNs = []
    for i in range(dbn_num):
        print(f"./inference/cpd/{infer_path}_{i}.cpd")
        with open(f"./inference/cpd/{infer_path}_{i}.cpd", 'r') as f:
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
                if len(clause_parts) > 0:
                    funs.append(" | ".join(clause_parts))
                else:
                    funs.append("(" + ") & (".join(v_pars) + ") & FALSE")
            
            infer_BN = BN(vars, funs)
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
            BNs.append(BN_params(infer_BN, vars, parents, MBs)) 
    return BNs   

def measure_distance(source_path: str, infer_path: str):
    source_BNs = parse_source(source_path)
    infer_BNs = parse_infer(infer_path, len(source_BNs))

    print(f'Comparing networks from test {infer_path}...')
    for num, (s, i) in enumerate(zip(source_BNs, infer_BNs)):
        print('\n==== TEST START ====\n\n')
        print(f'Network pair no. {num}\n')
        # Precision, Recall, F1 on parent sets.
        sum_prec = 0
        sum_recall = 0
        for v in s.vars:
            par_s = s.parents[v]
            par_i = i.parents[v]
            sum_prec   += len(set(par_s) & set(par_i)) / len(par_s)
            sum_recall += len(set(par_s) & set(par_i)) / len(par_i)
        sum_prec /= len(s.vars)
        sum_recall /= len(s.vars)
        sum_f1 = (2 * sum_prec * sum_recall) / (sum_recall + sum_prec)
        print(
            f"Scores on parent sets: Precision = {sum_prec}, "
            f"Recall = {sum_recall}, F1 = {sum_f1}\n"
        )

        # Precision, Recall, F1 on Markov Blankets
        sum_prec = 0
        sum_recall = 0
        for v in s.vars:
            par_s = s.MBs[v]
            par_i = i.MBs[v]
            sum_prec   += len(set(par_s) & set(par_i)) / len(par_s)
            sum_recall += len(set(par_s) & set(par_i)) / len(par_i)
        sum_prec /= len(s.vars)
        sum_recall /= len(s.vars)
        sum_f1 = (2 * sum_prec * sum_recall) / (sum_recall + sum_prec)
        print(
            f"Scores on Markov Blankets: Precision = {sum_prec}, "
            f"Recall = {sum_recall}, F1 = {sum_f1}\n"
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
        async_sum_prec = 0
        async_sum_recall = 0
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
            async_sum_prec   += len(async_n_s & async_n_i) / len(async_n_s)
            async_sum_recall += len(async_n_s & async_n_i) / len(async_n_i)

        async_sum_prec /= (2 ** state_size)
        async_sum_recall /= (2 ** state_size)
        sum_f1 = (2 * async_sum_prec * async_sum_recall) / (async_sum_recall + async_sum_prec)
        print(
            f"Scores on Asynchronous Neighbour States: Precision = {async_sum_prec}, "
            f"Recall = {async_sum_recall}, F1 = {sum_f1}\n"
        )


        print('\n==== TEST END ====\n')



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--source", type=str, required=True, help="File path to source Boolean Networks")
    parser.add_argument("-i", "--inference", type=str, required=True, help="File name prefix to inferenced DBNs")

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