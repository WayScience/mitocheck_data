# MitoCheck Data

## Data

### Access

All data are publicly available.

#### Confocal Microscopy

| Data | Level | Location | Notes |
| :---- | :---- | :------ | :---- |
| Images | 1 | Image Data Resource ([IDR](https://idr.openmicroscopy.org/)) | Accession `idr0013(screenA)` |

## Repository Structure:

This repository is structured as follows:

| Order | Module | Description |
| :---- | :----- | :---------- |
| [0.locate_data](0.locate_data/) | Locate mitosis movies | Find locations (plate, well, frame) for training and control movies |
| [1.idr_streams](1.idr_streams/) | Extract features from mitosis movies | Use `idrstream` to extract features from training and control movies |
| [2.format_training_data](2.format_training_data/) | Format training data | Compile metadata, phenotypic class, and feature data for Mitocheck-labeled movies |
| [3.normalize_data](3.normalize_data/) | Normalize data | Use UMAP to suggest batch effects are not dominant signal and normalize with data with negative controls as normalization population |
| [4.analyze_data](4.analyze_data/) | Analyze data | Analyze normalized data |

Other necessary folders/files:

| Folder/File | Description |
| :--------- | :---------- |
| [mitocheck_metadata](mitocheck_metadata/) | IDR curated metadata, `trainingset` file and `features` dataset necessary for locating Mitocheck-labeled training data |
| [utils](utils/) | Python files with functions used throughout repository |
| [mitocheck_data_env.yml](mitocheck_data_env.yml) | Environment file with packages necessary to process mitocheck data |

## Setup

Perform the following steps to set up the `mitocheck_data` environment necessary for processing data in this repository.

### Step 1: Create Mitocheck Environment

```sh
# Run this command to create the conda environment for mitocheck data processing

conda env create -f mitocheck_data_env.yml
```

### Step 2: Activate Mitocheck Environment

```sh
# Run this command to activate the conda environment for mitocheck data processing

conda activate mitocheck_data
```
