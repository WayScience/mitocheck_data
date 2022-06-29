# 4. Preprocess Features

In this module, we present our pipeline for preprocessing features.

### Feature Preprocessing

We use [PyCytominer](https://github.com/cytomining/pycytominer), commit [`eec910a`](https://github.com/cytomining/pycytominer/commit/eec910a636bf023f31a34348bd4c61138991c557), to normalize single-cell embeddings features.
We use PyCytominer's `normalize()` function to standardize features by removing the mean and scaling to unit variance.
For more information regarding this type of standardization, see [sklearn.preprocessing.StandardScaler](https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.StandardScaler.html).

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
