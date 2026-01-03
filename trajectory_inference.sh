#!/bin/bash

if [ $# -ne 2 ]; then
    echo "Usage: $0 <output_prefix> <test_prefix>"
    exit 1
fi

output_prefix="$1"
test_prefix="$2"

mkdir -p inference

find ./datasets -type f -name "${test_prefix}_bn_*_trajectories.txt" | while read -r file; do
    if [[ "$file" =~ ${test_prefix}_bn_([0-9]+)_trajectories\.txt$ ]]; then
        num="${BASH_REMATCH[1]}"
        output_file="inference/${output_prefix}_${num}.sif"
        bnf -e "$file" -n "$output_file" -v
    fi
done