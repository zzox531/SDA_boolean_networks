#!/bin/bash

usage() {
    echo "Usage: $0 <output_prefix> <test_prefix> BDE <prior-pseudocount>"
    echo "       $0 <output_prefix> <test_prefix> MDL"
    exit 1
}

if [ $# -lt 3 ]; then
    usage
fi

output_prefix="$1"
test_prefix="$2"
criterion="$3"

if [ "$criterion" == "BDE" ]; then
    if [ $# -ne 4 ]; then
        echo "Error: BDE criterion requires a prior-pseudocount argument"
        usage
    fi
    prior="$4"
elif [ "$criterion" == "MDL" ]; then
    if [ $# -ne 3 ]; then
        echo "Error: MDL criterion does not take additional arguments"
        usage
    fi
else
    echo "Error: Invalid scoring criterion. Must be BDE or MDL"
    usage
fi

mkdir -p inference
mkdir -p inference/bif
mkdir -p inference/sif
mkdir -p inference/cpd

find ./datasets -type f -name "${test_prefix}_bn_*_trajectories.txt" | while read -r file; do
    if [[ "$file" =~ ${test_prefix}_bn_([0-9]+)_trajectories\.txt$ ]]; then
        num="${BASH_REMATCH[1]}"
        output_file_sif="inference/sif/${output_prefix}-${num}.sif"
        output_file_cpd="inference/cpd/${output_prefix}-${num}.cpd"

        if [ "$criterion" == "BDE" ]; then
            bnf -e "$file" -n "$output_file_sif" -c "$output_file_cpd" -v -s "$criterion" -p "$prior" -g -l 3 -k 16
        else
            bnf -e "$file" -n "$output_file_sif" -c "$output_file_cpd" -v -s "$criterion" -g -l 3 -k 16
        fi
    fi
done