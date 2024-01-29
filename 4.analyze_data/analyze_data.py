#!/usr/bin/env python
# coding: utf-8

# ### Import libraries
# 

# In[1]:


import pathlib
import pandas as pd
import seaborn as sns
from matplotlib.colors import rgb2hex

import sys

sys.path.append("../utils")
from load_utils import split_data
from analysis_utils import get_class_colors, show_1D_umap, show_2D_umap


# ### Set training data load path, dataset types, save directory

# In[2]:


# training data load path
training_data_dir = pathlib.Path(
    "../3.normalize_data/normalized_data/"
)

# dataset types
dataset_types = ["ic", "no_ic"]

# feature types to create umaps for
feature_types = ["CP", "DP", "CP_and_DP"]

# results directory
results_dir = pathlib.Path("results/")
results_dir.mkdir(parents=True, exist_ok=True)


# ### Set UMAP display settings and class colors
# 

# In[3]:


point_size = 25
alpha = 0.6
color_palette = "bright"

classes_1 = [
    "Large",
    "Prometaphase",
    "Grape",
    "Interphase",
    "Apoptosis",
    "ADCCM",
    "Folded",
    "SmallIrregular",
    "Polylobed",
    "Metaphase",
    "Binuclear",
    "Hole",
    "Anaphase",
    "MetaphaseAlignment",
    "Elongated",
    "OutOfFocus",
]

# classes that aren't commented out will get a color for their particular class
# those that are commented out will be colored gray and labeled "other"
classes_2 = [
    # "Large",
    "Prometaphase",
    "Grape",
    "Interphase",
    "Apoptosis",
    "ADCCM",
    # "Folded",
    # "SmallIrregular",
    # "Polylobed",
    # "Metaphase",
    # "Binuclear",
    # "Hole",
    # "Anaphase",
    # "MetaphaseAlignment",
    # "Elongated",
    # "OutOfFocus",
]

class_colors_1 = get_class_colors(classes_1, "rainbow")
class_colors_2 = get_class_colors(classes_2, "bright")


# In[4]:


# list to compile cell counts tidy data
compiled_single_cell_class_counts = []

# list to compile embeddings tidy data
compiled_tidy_embeddings = []

for dataset_type in dataset_types:
    
    # load training data
    training_data_path = pathlib.Path(
        f"{training_data_dir}/training_data__{dataset_type}.csv.gz"
    )
    training_data = pd.read_csv(training_data_path, compression="gzip", index_col=0)
    
    # save single-cell counts per phenotype
    # get single-cell class counts
    single_cell_class_counts = (
        training_data["Mitocheck_Phenotypic_Class"]
        .value_counts()
        .rename_axis("Mitocheck_Phenotypic_Class")
        .reset_index(name="Single_Cell_Counts")
    )
    single_cell_class_counts["Dataset_Type"] = dataset_type
    
    # add these single cell counts to compilation
    compiled_single_cell_class_counts.append(single_cell_class_counts)
    
    # create umaps for each feature type
    for feature_type in feature_types:
        print(f"Showing UMAPs created with {feature_type} features")

        # the trainind data dataframe is split into two components:
        # metadata: info about the cell including its labeled phenotypic class, location, perturbation, etc
        # feature data: the CP, DP, or merged features for each cell
        metadata_dataframe, feature_data = split_data(training_data, feature_type)
        phenotypic_classes = metadata_dataframe["Mitocheck_Phenotypic_Class"]

        # show 2D umaps
        # class colors 1 - all classes included
        embeddings_2D = show_2D_umap(
            feature_data,
            phenotypic_classes,
            class_colors_1,
            point_size=point_size,
            alpha=alpha,
        )

        # add feature types column for tidy long data
        embeddings_2D["Dataset_Type"] = dataset_type
        # add feature types column for tidy long data
        embeddings_2D["Feature_Type"] = feature_type
        # add cell UUID types column for tidy long data
        embeddings_2D["Cell_UUID"] = metadata_dataframe["Cell_UUID"]
        # melt embeddings data into tidy format
        embeddings_2D = pd.melt(
            embeddings_2D,
            id_vars=["Mitocheck_Phenotypic_Class", "Dataset_Type", "Feature_Type", "Cell_UUID"],
            value_vars=["UMAP1", "UMAP2"],
            var_name="UMAP_Embedding",
            value_name="Embedding_Value",
        )

        # add these tidy embeddings to compilation
        compiled_tidy_embeddings.append(embeddings_2D)


# ### Save and preview tidy single-cell class counts

# In[5]:


# compile tidy embeddings into one dataframe
compiled_single_cell_class_counts = pd.concat(compiled_single_cell_class_counts).reset_index(drop=True)

# save single-cell class counts
single_cell_class_counts_save_path = pathlib.Path(
    f"{results_dir}/single_cell_class_counts.csv"
)
compiled_single_cell_class_counts.to_csv(single_cell_class_counts_save_path)

# preview single-cell class counts
compiled_single_cell_class_counts


# ### Save and preview tidy embedding data
# 

# In[6]:


# compile tidy embeddings into one dataframe
compiled_tidy_embeddings = pd.concat(compiled_tidy_embeddings).reset_index(drop=True)

# save tidy embeddings
compiled_tidy_embeddings_save_path = pathlib.Path(
    f"{results_dir}/compiled_2D_umap_embeddings.csv"
)
compiled_tidy_embeddings.to_csv(compiled_tidy_embeddings_save_path)

# preview tidy embeddings data
compiled_tidy_embeddings

