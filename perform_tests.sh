#!/bin/bash

set -e

# configs: "ratio_lo ratio_hi fr_lo fr_hi len_lo len_hi sync_no async_no test_prefix seed criterion"
configs=(
    "0.2 0.4 1 1 10 50 100 0 test0 42 BDE"
    "0.2 0.4 1 1 10 50 100 0 test1 42 BDE"
)

BN_PREF="datasets/bn_"

mkdir -p datasets logs inference

for conf in "${configs[@]}"; do
    set -- $conf
    ratio_lo=$1; ratio_hi=$2; fr_lo=$3; fr_hi=$4; len_lo=$5; len_hi=$6
    sync_no=$7; async_no=$8; test_prefix=$9; seed=${10}
    criterion=${11}

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
    ./trajectory_inference.sh "$test_prefix" "$test_prefix" "$criterion"

    echo "--- Completed $test_prefix ---"
    echo
done

echo "=== ALL TESTS COMPLETE ==="