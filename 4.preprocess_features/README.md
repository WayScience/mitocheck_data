# 4. Preprocess Features

In this module, we present our pipeline for preprocessing features.
### Feature Preprocessing

We use [PyCytominer](https://github.com/cytomining/pycytominer), commit [`fcf03b6`](https://github.com/cytomining/pycytominer/commit/fcf03b60e7591b45e82acd6662d6bb0182f8f1cf), to normalize single-cell embeddings features.



## Step 1: Setup Feature Preprocessing Environment

### Step 1a: Create Feature Preprocessing Environment

```sh
# Run this command to create the conda environment for preprocessing features
conda env create -f 4.preprocess_features_env.yml
```

### Step 1b: Activate Preprocessing Environment

```sh
# Run this command to activate the conda environment for preprocessing features
conda activate 4.preprocess_features_mitocheck
```

## Step 2: Normalize Single Cell Training Features

```bash
# Run this script to preprocess training features
bash 4.preprocess_training_features.sh
```
