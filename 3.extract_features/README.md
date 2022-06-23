# 3. Extract Features

In this module, we present our pipeline for extracting features from the mitosis movies.

### Feature Extraction

We use [DeepProfiler](https://github.com/cytomining/DeepProfiler), commit [`2fb3ed3`](https://github.com/cytomining/DeepProfiler/commit/2fb3ed3027cded6676b7e409687322ef67491ec7), to extract features from the mitosis movies. 

We use a [pretrained model](https://github.com/broadinstitute/luad-cell-painting/tree/main/outputs/efn_pretrained/checkpoint) from the [LUAD Cell Painting repository](https://github.com/broadinstitute/luad-cell-painting) with DeepProfiler.
[Caicedo et al., 2022](https://www.molbiolcell.org/doi/10.1091/mbc.E21-11-0538) trained this model to extract features from Cell Painting data.
This model extracts features from the DNA (nuclei) channel and is thus a good selection for our use case.

## Step 1: Setup Feature Extraction Environment

### Step 1a: Create Feature Extraction Environment

```sh
# Run this command to create the conda environment for Segmentation data
conda env create -f 2.feature_extraction_env.yml
```

### Step 1b: Activate Feature Extraction Environment


```sh
# Run this command to activate the conda environment for Segmentation data
conda activate 3.feature_extraction_mitocheck
```

## Step 2: Install DeepProfiler

### Step 2a: Clone Resository
Clone the DeepProfiler repository into 3.extract_features/ with 

```console
git clone https://github.com/cytomining/DeepProfiler.git
```

### Step 2b: Install Resository
Install the DeepProfiler repository with

```console
cd DeepProfiler/
pip install -e .
```

### Step 2c (Optional): Complete Tensorflow GPU Setup

If you would like use Tensorflow GPU when using DeepProfiler, follow [these instructions](https://www.tensorflow.org/install/pip#3_gpu_setup) to complete the Tensorflow GPU setup.
We use Tensorflow GPU while processing mitocheck data.

## Step 3: Compile DeepProfiler Project

```bash
# Run this script to compile the DeepProfiler project
bash 3.compile_deepprof__training_proj.sh
```

## Step 4: Extract Features with DeepProfiler

```sh
# Run this script to extract features with DeepProfiler
python3 -m deepprofiler --gpu 0 --exp efn_pretrained --root ./ --config mitocheck_profiling_config.json profile
```