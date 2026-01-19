#!/bin/bash

set -e

# configs: "ratio_lo ratio_hi fr_lo fr_hi len_lo len_hi sync_no async_no test_prefix seed criterion"
configs=(
    "0.4 0.6 1 1  25  25 10 0    len_small-025-sync 42"
    "0.4 0.6 1 1  50  50 10 0    len_small-050-sync 42"
    "0.4 0.6 1 1  75  75 10 0    len_small-075-sync 42"
    "0.4 0.6 1 1 100 100 10 0    len_small-100-sync 42"
    "0.4 0.6 1 1 125 125 10 0    len_small-125-sync 42"
    "0.4 0.6 1 1 150 150 10 0    len_small-150-sync 42"
    "0.4 0.6 1 1 175 175 10 0    len_small-175-sync 42"
    "0.4 0.6 1 1 200 200 10 0    len_small-200-sync 42"
    "0.4 0.6 1 1 225 225 10 0    len_small-225-sync 42"
    "0.4 0.6 1 1 250 250 10 0    len_small-250-sync 42"
    "0.4 0.6 1 1 275 275 10 0    len_small-275-sync 42"
    "0.4 0.6 1 1 300 300 10 0    len_small-300-sync 42"
    "0.0 0.1 1 1 50 300  10 0  ratio_small-0.1-sync 42"
    "0.1 0.2 1 1 50 300  10 0  ratio_small-0.2-sync 42"
    "0.2 0.3 1 1 50 300  10 0  ratio_small-0.3-sync 42"
    "0.3 0.4 1 1 50 300  10 0  ratio_small-0.4-sync 42"
    "0.4 0.5 1 1 50 300  10 0  ratio_small-0.5-sync 42"
    "0.5 0.6 1 1 50 300  10 0  ratio_small-0.6-sync 42"
    "0.6 0.7 1 1 50 300  10 0  ratio_small-0.7-sync 42"
    "0.7 0.8 1 1 50 300  10 0  ratio_small-0.8-sync 42"
    "0.8 0.9 1 1 50 300  10 0  ratio_small-0.9-sync 42"
    "0.9 1.0 1 1 50 300  10 0  ratio_small-1.0-sync 42"
    "0.4 0.6 1 1  25  25 0 10   len_small-025-async 42"
    "0.4 0.6 1 1  50  50 0 10   len_small-050-async 42"
    "0.4 0.6 1 1  75  75 0 10   len_small-075-async 42"
    "0.4 0.6 1 1 100 100 0 10   len_small-100-async 42"
    "0.4 0.6 1 1 125 125 0 10   len_small-125-async 42"
    "0.4 0.6 1 1 150 150 0 10   len_small-150-async 42"
    "0.4 0.6 1 1 175 175 0 10   len_small-175-async 42"
    "0.4 0.6 1 1 200 200 0 10   len_small-200-async 42"
    "0.4 0.6 1 1 225 225 0 10   len_small-225-async 42"
    "0.4 0.6 1 1 250 250 0 10   len_small-250-async 42"
    "0.4 0.6 1 1 275 275 0 10   len_small-275-async 42"
    "0.4 0.6 1 1 300 300 0 10   len_small-300-async 42"
    "0.0 0.1 1 1 50 300  0 10 ratio_small-0.1-async 42"
    "0.1 0.2 1 1 50 300  0 10 ratio_small-0.2-async 42"
    "0.2 0.3 1 1 50 300  0 10 ratio_small-0.3-async 42"
    "0.3 0.4 1 1 50 300  0 10 ratio_small-0.4-async 42"
    "0.4 0.5 1 1 50 300  0 10 ratio_small-0.5-async 42"
    "0.5 0.6 1 1 50 300  0 10 ratio_small-0.6-async 42"
    "0.6 0.7 1 1 50 300  0 10 ratio_small-0.7-async 42"
    "0.7 0.8 1 1 50 300  0 10 ratio_small-0.8-async 42"
    "0.8 0.9 1 1 50 300  0 10 ratio_small-0.9-async 42"
    "0.9 1.0 1 1 50 300  0 10 ratio_small-1.0-async 42"
)

_PREF="datasets/bn_"

mkdir -p datasets logs inference

for conf in "${configs[@]}"; do
    set -- $conf
    ratio_lo=$1; ratio_hi=$2; fr_lo=$3; fr_hi=$4; len_lo=$5; len_hi=$6
    sync_no=$7; async_no=$8; test_prefix=$9; seed=${10}

    tg_json="datasets/${test_prefix}_trajs_bn_"
    log_file="logs/traj_gen_${test_prefix}.log"
    out_prefix="inference/${test_prefix}"

    echo "=== Generating trajectories for $test_prefix ==="
    python3 trajectory_generator.py \
        -ratio-lo $ratio_lo \
        -ratio-hi $ratio_hi \
        -fr-lo $fr_lo \
        -fr-hi $fr_hi \
        -len-lo $len_lo \
        -len-hi $len_hi \
        -sync-no $sync_no \
        -async-no $async_no \
        -bn-ds "$BN_PREF" \
        -tg-ds "$tg_json" \
        -tg-ds-txt "datasets/${test_prefix}" \
        -lf "$log_file" \
        -s $seed

    echo "=== Running inference for $test_prefix ==="
    ./trajectory_inference.sh "${test_prefix}-BDE" "$test_prefix" "BDE"
    ./trajectory_inference.sh "${test_prefix}-MDL" "$test_prefix" "MDL"

    echo "--- Completed $test_prefix ---"
    echo
done

echo "=== ALL TESTS COMPLETE ==="