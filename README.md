# MitoCheck Data

## Data

### Access

All data are publicly available.

#### Confocal Microscopy

| Data | Level | Location | Notes |
| :---- | :---- | :------ | :---- |
| Images | 1 | Image Data Resource ([IDR](https://idr.openmicroscopy.org/)) | Accession `idr0013(screenA)` |


## Pipeline:

The movie processing pipeline consists of the following steps:

| Order | Module | Description |
| :---- | :----- | :---------- |
| [0.locate_data](0.locate_data/) | Locate mitosis movies | Find locations (plate, well, frame) for training and control movies |
| [1.idr_streams](1.idr_streams/) | Extract features from mitosis movies | Use `idrstream` to extract features from training and control movies |
| [2.format_training_data](2.format_training_data/) | Format training data | Compile metadata, phenotypic class, and feature data for Mitocheck-labeled movies |
| [3.normalize_data](3.normalize_data/) | Normalize data | Use UMAP to suggest batch effects are not dominant signal and normalize with data with negative controls as normalization population |
| [4.analyze_data](4.analyze_data/) | Analyze data | Analyze normalized data |
