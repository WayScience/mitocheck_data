# 0. Locate Data

In this module, we curate metadata (plate, well, frame, gene) for Mitocheck-labeled training and control movies.
These metadata will be used as input to `idrstream` to indicate where `idrstream` should extract features from.

## Step 1: Locate Data

Use the commands below to locate training and control movies:

```sh
# Make sure you are located in 0.locate_data
cd 0.locate_data

# Activate mitocheck_data conda environment
conda activate mitocheck_data

# Locate data
bash locate_data.sh
```
