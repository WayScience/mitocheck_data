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
| [3.normalize_data](3.normalize_data/) | Normalize data | Use UMAP to suggest batch effects are not dominant signal and normalize with data using negative controls as normalization population |
| [4.analyze_data](4.analyze_data/) | Analyze data | Analyze normalized data |

Other necessary folders/files:

| Folder/File | Description |
| :--------- | :---------- |
| [mitocheck_metadata](mitocheck_metadata/) | IDR curated metadata, `trainingset` file and `features` dataset necessary for locating Mitocheck-labeled training data |
| [utils](utils/) | Python files with functions used throughout repository |
| [mitocheck_data_env.yml](mitocheck_data_env.yml) | Environment file with packages necessary to process mitocheck data |

## Training Data

As part of the [Phenotypic profiling of the human genome by time-lapse microscopy reveals cell division genes](https://www.nature.com/articles/nature08869), Mitocheck created a training dataset with cell phenotypic classes and their locations.
This dataset was provided by J.K. Hériché and is located in [mitocheck_metadata](mitocheck_metadata).
This dataset contains the following files:

- [trainingset.dat](mitocheck_metadata/trainingset_2007_06_21.dat) : Mitocheck-assigned object IDs and phenotypic class for cells from a specified frame, well, and plate.
- [features/](mitocheck_metadata/features) : Mitocheck-assigned object IDs and bounding boxes for cells from a specified frame, well, and plate.

We use `trainingset.dat` to locate the frame, well, and plate of labeled cells in [0.locate_data](0.locate_data/).
After extracting the features from these labeled frames with `idrstream`, we associate the bounding boxes of cells from `features/` with their `idrstream`-derived coordinates to assign cells their phenotypic class (as labeled by Mitocheck).

## Control Data

We extract single-cell features from positive and negative controls, which are useful for normalizing all Mitocheck data and suggesting that batch effects are not a dominant signal.

We use [IDR-curated mitocheck metadata](mitocheck_metadata/idr0013-screenA-annotation.csv.gz) to locate the well and plate of each control movie.
Because `idrstream` can only extract features from a single frame, we choose a random frame from the middle 33% of the movie.
Mitocheck mitosis movies are about 93 frames long, so a random frame between frames 31 and 62 are chosen to extract features from.
Because we cannot exactly align the movies in time, we opt to randomly sample from the middle of the movies.

## Dataset Types

We extract all single-cell features with and without illumination correction.
We refer to these dataset types in the code as `dataset_type`, where `ic` corresponds to the dataset with illumination correction and `no_ic` corresponds to the dataset without illumination correction.

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
