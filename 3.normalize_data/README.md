# 3. Normalize Data

In this module, we use [UMAP](https://github.com/lmcinnes/umap) on control data to suggest batch effects are not the dominant signal in the mitosis movies.
UMAP was introduced in [McInnes, L, Healy, J, 2018](https://arxiv.org/abs/1802.03426) as a manifold learning technique for dimension reduction.
We use UMAP to reduce the feature data from 1280 features to 2 dimensions.

As shown in [controls_Metadata_Gene.png](raw_data_umaps/controls_Metadata_Gene.png), UMAP tends to group features based on their gene.
This demonstrates that the biological changes induced by gene pertubations have manifested in the `DeepProfiler` features extracted with `idrstream`.
The other UMAPs in [raw_data_umaps/](raw_data_umaps/) suggest that batch effects from plate, well, and frame are not the dominant signal in the feature data.

**Note:** UMAPs were generated with 10% of data from positive and negative controls.

Next, we derive a normalization scaler with [sklearn.preprocessing.StandardScaler](https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.StandardScaler.html) from the negative control features.
[Caicedo et al, 2017](https://www.nature.com/articles/nmeth.4397) explain why the negative control features are a good normalization population for our use case:
> When choosing the normalizing population, we suggest the use of control samples (assuming that they are present in sufficient quantity), because the presence of dramatic phenotypes may confound results. This procedure is good practice regardless of the normalization being performed within plates or across the screen.

Because batch effects are likely not the dominant signal in the mitosis movies, we perform normalization across the entire screen.
In other words, we create one normalization scaler from all negative control features and apply this normalization scaler to all mitosis movie feature data.

## Step 1: Generate Raw Data UMAPs and Normalize Data

Use the commands below to generate raw data UMAPs and normalize all data.
All normalized data will be saved to [normalized_data/](normalized_data/).
Only the normalized training data has been uploaded to github as the positive and negative control datasets are too large.

```sh
# Make sure you are located in 3.normalize_data
cd 3.normalize_data

# Activate mitocheck_data conda environment
conda activate mitocheck_data

# Generate raw data UMAPs and normalize all data
bash normalize_data.sh
```
