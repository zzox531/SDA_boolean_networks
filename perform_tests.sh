#!/bin/bash

set -e

# configs: "fr_lo fr_hi len_lo len_hi sync_no async_no test_prefix seed"
configs=(
    "1 1 10 50 50 50 test0 42 BDE"
    # "1 1 10 50 0 50 test1 42 BDE"
    # "1 1 10 50 50 0 test2 42 BDE"
)
BN_JSON="datasets/boolean_networks.json"

mkdir -p datasets logs inference

for conf in "${configs[@]}"; do
    set -- $conf
    fr_lo=$1; fr_hi=$2; len_lo=$3; len_hi=$4
    sync_no=$5; async_no=$6; test_prefix=$7; seed=$8
    criterion=$9

    tg_json="datasets/${test_prefix}_trajectory_samples.json"
    log_file="logs/traj_gen_${test_prefix}.log"
    out_prefix="inference/${test_prefix}"

    echo "=== Generating trajectories for $test_prefix ==="
    python3 trajectory_generator.py \
        -fr-lo $fr_lo \
        -fr-hi $fr_hi \
        -len-lo $len_lo \
        -len-hi $len_hi \
        -sync-no $sync_no \
        -async-no $async_no \
        -bn-ds "$BN_JSON" \
        -tg-ds "$tg_json" \
        -tg-ds-txt "datasets/${test_prefix}" \
        -lf "$log_file" \
        -s $seed

    echo "=== Running inference for $test_prefix ==="
    ./trajectory_inference.sh "$test_prefix" "$test_prefix" "$criterion"

    echo "--- Completed $test_prefix ---"
    echo
done

echo "=== ALL TESTS COMPLETE ==="