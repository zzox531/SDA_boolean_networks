#!/bin/bash

set -e

BN_PREF="chicken_dataset/bn_"

mkdir -p logs chicken_inference

ratio_lo=0.5
ratio_hi=0.5
fr_lo=1
fr_hi=1
len_lo=40
len_hi=100
sync_no=25
async_no=0
seed=42

tg_json="chicken_dataset/chicken_bn_"
log_file="logs/chicken.log"

echo "=== Generating trajectories for chicken test ==="
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
    -tg-ds-txt "chicken_dataset/chicken" \
    -lf "$log_file" \
    -s $seed

echo "=== Running inference for chicken test ==="

mkdir -p chicken_inference
mkdir -p chicken_inference/sif
mkdir -p chicken_inference/cpd

output_file_BDE_sif="chicken_inference/sif/chicken_test-BDE-sync-0.sif"
output_file_BDE_cpd="chicken_inference/cpd/chicken_test-BDE-sync-0.cpd"

output_file_MDL_sif="chicken_inference/sif/chicken_test-MDL-sync-0.sif"
output_file_MDL_sif="chicken_inference/cpd/chicken_test-MDL-sync-0.cpd"

bnf -e "chicken_dataset/chicken_bn_0_trajectories.txt" -n "$output_file_BDE_sif" -c "$output_file_BDE_cpd" -v -s "BDE" -g -l 3 -k 16
bnf -e "chicken_dataset/chicken_bn_0_trajectories.txt" -n "$output_file_MDL_sif" -c "$output_file_MDL_cpd" -v -s "MDL" -g -l 3 -k 16

echo "=== CHICKEN INFERENCE COMPLETE ==="