#!/bin/bash

set -e

# configs: "ratio_lo ratio_hi fr_lo fr_hi len_lo len_hi sync_no async_no test_prefix seed criterion"
configs=(
    "0.5 0.5 1 1   5   5 25 0    len-005-sync 42"
    "0.5 0.5 1 1  10  10 25 0    len-010-sync 42"
    "0.5 0.5 1 1  15  15 25 0    len-015-sync 42"
    "0.5 0.5 1 1  20  20 25 0    len-020-sync 42"
    "0.5 0.5 1 1  25  25 25 0    len-025-sync 42"
    "0.5 0.5 1 1  30  30 25 0    len-030-sync 42"
    "0.5 0.5 1 1  35  35 25 0    len-035-sync 42"
    "0.5 0.5 1 1  40  40 25 0    len-040-sync 42"
    "0.5 0.5 1 1  45  45 25 0    len-045-sync 42"
    "0.5 0.5 1 1  50  50 25 0    len-050-sync 42"
    "0.5 0.5 1 1  55  55 25 0    len-055-sync 42"
    "0.5 0.5 1 1  60  60 25 0    len-060-sync 42"
    "0.5 0.5 1 1  65  65 25 0    len-065-sync 42"
    "0.5 0.5 1 1  70  70 25 0    len-070-sync 42"
    "0.5 0.5 1 1  75  75 25 0    len-075-sync 42"
    "0.5 0.5 1 1  80  80 25 0    len-080-sync 42"
    "0.5 0.5 1 1  85  85 25 0    len-085-sync 42"
    "0.5 0.5 1 1  90  90 25 0    len-090-sync 42"
    "0.5 0.5 1 1  95  95 25 0    len-095-sync 42"
    "0.5 0.5 1 1 100 100 25 0    len-100-sync 42"
    "0.5 0.5 1 1   5   5 0 25    len-005-async 42"
    "0.5 0.5 1 1  10  10 0 25    len-010-async 42"
    "0.5 0.5 1 1  15  15 0 25    len-015-async 42"
    "0.5 0.5 1 1  20  20 0 25    len-020-async 42"
    "0.5 0.5 1 1  25  25 0 25    len-025-async 42"
    "0.5 0.5 1 1  30  30 0 25    len-030-async 42"
    "0.5 0.5 1 1  35  35 0 25    len-035-async 42"
    "0.5 0.5 1 1  40  40 0 25    len-040-async 42"
    "0.5 0.5 1 1  45  45 0 25    len-045-async 42"
    "0.5 0.5 1 1  50  50 0 25    len-050-async 42"
    "0.5 0.5 1 1  55  55 0 25    len-055-async 42"
    "0.5 0.5 1 1  60  60 0 25    len-060-async 42"
    "0.5 0.5 1 1  65  65 0 25    len-065-async 42"
    "0.5 0.5 1 1  70  70 0 25    len-070-async 42"
    "0.5 0.5 1 1  75  75 0 25    len-075-async 42"
    "0.5 0.5 1 1  80  80 0 25    len-080-async 42"
    "0.5 0.5 1 1  85  85 0 25    len-085-async 42"
    "0.5 0.5 1 1  90  90 0 25    len-090-async 42"
    "0.5 0.5 1 1  95  95 0 25    len-095-async 42"
    "0.5 0.5 1 1 100 100 0 25    len-100-async 42"
    "0.05 0.05 1 1 10 50  25 0  ratio-0.05-sync 42"
    "0.10 0.10 1 1 10 50  25 0  ratio-0.10-sync 42"
    "0.15 0.15 1 1 10 50  25 0  ratio-0.15-sync 42"
    "0.20 0.20 1 1 10 50  25 0  ratio-0.20-sync 42"
    "0.25 0.25 1 1 10 50  25 0  ratio-0.25-sync 42"
    "0.30 0.30 1 1 10 50  25 0  ratio-0.30-sync 42"
    "0.35 0.35 1 1 10 50  25 0  ratio-0.35-sync 42"
    "0.40 0.40 1 1 10 50  25 0  ratio-0.40-sync 42"
    "0.45 0.45 1 1 10 50  25 0  ratio-0.45-sync 42"
    "0.50 0.50 1 1 10 50  25 0  ratio-0.50-sync 42"
    "0.55 0.55 1 1 10 50  25 0  ratio-0.55-sync 42"
    "0.60 0.60 1 1 10 50  25 0  ratio-0.60-sync 42"
    "0.65 0.65 1 1 10 50  25 0  ratio-0.65-sync 42"
    "0.70 0.70 1 1 10 50  25 0  ratio-0.70-sync 42"
    "0.75 0.75 1 1 10 50  25 0  ratio-0.75-sync 42"
    "0.80 0.80 1 1 10 50  25 0  ratio-0.80-sync 42"
    "0.85 0.85 1 1 10 50  25 0  ratio-0.85-sync 42"
    "0.90 0.90 1 1 10 50  25 0  ratio-0.90-sync 42"
    "0.95 0.95 1 1 10 50  25 0  ratio-0.95-sync 42"
    "1.00 1.00 1 1 10 50  25 0  ratio-1.00-sync 42"
    "0.05 0.05 1 1 10 50  0 25  ratio-0.05-async 42"
    "0.10 0.10 1 1 10 50  0 25  ratio-0.10-async 42"
    "0.15 0.15 1 1 10 50  0 25  ratio-0.15-async 42"
    "0.20 0.20 1 1 10 50  0 25  ratio-0.20-async 42"
    "0.25 0.25 1 1 10 50  0 25  ratio-0.25-async 42"
    "0.30 0.30 1 1 10 50  0 25  ratio-0.30-async 42"
    "0.35 0.35 1 1 10 50  0 25  ratio-0.35-async 42"
    "0.40 0.40 1 1 10 50  0 25  ratio-0.40-async 42"
    "0.45 0.45 1 1 10 50  0 25  ratio-0.45-async 42"
    "0.50 0.50 1 1 10 50  0 25  ratio-0.50-async 42"
    "0.55 0.55 1 1 10 50  0 25  ratio-0.55-async 42"
    "0.60 0.60 1 1 10 50  0 25  ratio-0.60-async 42"
    "0.65 0.65 1 1 10 50  0 25  ratio-0.65-async 42"
    "0.70 0.70 1 1 10 50  0 25  ratio-0.70-async 42"
    "0.75 0.75 1 1 10 50  0 25  ratio-0.75-async 42"
    "0.80 0.80 1 1 10 50  0 25  ratio-0.80-async 42"
    "0.85 0.85 1 1 10 50  0 25  ratio-0.85-async 42"
    "0.90 0.90 1 1 10 50  0 25  ratio-0.90-async 42"
    "0.95 0.95 1 1 10 50  0 25  ratio-0.95-async 42"
    "1.00 1.00 1 1 10 50  0 25  ratio-1.00-async 42"
    "0.5 0.5  1  1 10 50  25 0  freq-01-sync 42"
    "0.5 0.5  2  2 10 50  25 0  freq-02-sync 42"
    "0.5 0.5  3  3 10 50  25 0  freq-03-sync 42"
    "0.5 0.5  4  4 10 50  25 0  freq-04-sync 42"
    "0.5 0.5  5  5 10 50  25 0  freq-05-sync 42"
    "0.5 0.5  6  6 10 50  25 0  freq-06-sync 42"
    "0.5 0.5  7  7 10 50  25 0  freq-07-sync 42"
    "0.5 0.5  8  8 10 50  25 0  freq-08-sync 42"
    "0.5 0.5  9  9 10 50  25 0  freq-09-sync 42"
    "0.5 0.5 10 10 10 50  25 0  freq-10-sync 42"
    "0.5 0.5  1  1 10 50  0 25  freq-01-async 42"
    "0.5 0.5  2  2 10 50  0 25  freq-02-async 42"
    "0.5 0.5  3  3 10 50  0 25  freq-03-async 42"
    "0.5 0.5  4  4 10 50  0 25  freq-04-async 42"
    "0.5 0.5  5  5 10 50  0 25  freq-05-async 42"
    "0.5 0.5  6  6 10 50  0 25  freq-06-async 42"
    "0.5 0.5  7  7 10 50  0 25  freq-07-async 42"
    "0.5 0.5  8  8 10 50  0 25  freq-08-async 42"
    "0.5 0.5  9  9 10 50  0 25  freq-09-async 42"
    "0.5 0.5 10 10 10 50  0 25  freq-10-async 42"
)

BN_PREF="datasets/bn_"

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