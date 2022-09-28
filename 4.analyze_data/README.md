# 4. Analyze Data

In this module, we analyze the normalized training data features from [3.normalize_data](../3.normalize_data/normalized_data/training_data.csv.gz).

### Feature Analysis

We use [UMAP](https://github.com/lmcinnes/umap) for analyis of features.
UMAP was introduced in [McInnes, L, Healy, J, 2018](https://arxiv.org/abs/1802.03426) as a manifold learning technique for dimension reduction.
We use UMAP to reduce the feature data from 1280 features to 1, 2, and 3 dimensions.
We use [Matplotlib](https://matplotlib.org/) to visualize the 1D, 2D, and 3D UMAPS.

For each reduction with UMAP, we create two types of visualizations.
The first visualization colors all points by their phenotypic class.
The second visualization colors points for only certain phenotypic classes, with all other phenotypic classes being colored gray.

**Note:** Phenotypic classes colored in second visualization can be changed with the `classes_2 = [
` variable in [analyze_data.ipynb](analyze_data.ipynb).

## Step 1: Analyze Data

Use the commands below to analyze training data.
All UMAPs will be saved to [umaps/](umaps/).

```sh
# Make sure you are located in 4.analyze_data
cd 4.analyze_data

# Activate mitocheck_data conda environment
conda activate mitocheck_data

# Analyze data
bash analyze_data.sh
```
