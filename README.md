# Boolean Network Reconstruction

This is the repository for the Statistical Data Analysis Project for 2025/26 SDA Bioinformatics course @ MIMUW.

## Random BN Generation

Random BN generation is possible via `bn_generator.py` script. The script generates a list of variable nodes and corresponding boolean functions, and stores them in a `.json` file.

Usage:

```sh
python bn_generator.py [-s SEED] count ds_filename
```

Parameters:

- SEED - Set RNG seed for controlling output
- count - Number of BNs to generate
- ds_filename - Name of a `.json` file to store the BNs to.