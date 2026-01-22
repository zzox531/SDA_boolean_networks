#!/bin/bash

if [ $# -ne 3 ]; then
    echo "Usage: $0 <output_prefix> <test_prefix> <scoring criterion: BDE | MDL>"
    exit 1
fi

output_prefix="$1"
test_prefix="$2"
criterion="$3"

mkdir -p inference
mkdir -p inference/sif
mkdir -p inference/cpd

find ./datasets -type f -name "${test_prefix}_bn_*_trajectories.txt" | while read -r file; do
    if [[ "$file" =~ ${test_prefix}_bn_([0-9]+)_trajectories\.txt$ ]]; then
        num="${BASH_REMATCH[1]}"
        output_file_sif="inference/sif/${output_prefix}-${num}.sif"
        output_file_cpd="inference/cpd/${output_prefix}-${num}.cpd"
        bnf -e "$file" -n "$output_file_sif" -c "$output_file_cpd" -v -s "$criterion" -g -l 3 -k 16
    fi
done