#!/usr/bin/env python
# coding: utf-8

# ### Import libraries

# In[1]:


import pathlib
import pandas as pd

import sys
sys.path.append("../utils")
from load_utils import split_data
from analysis_utils import get_2D_umap_embeddings, show_1D_umap, show_2D_umap, show_3D_umap


# ### Load training data, see class counts

# In[2]:


training_data_path = pathlib.Path("../3.normalize_data/normalized_data/training_data.csv.gz")
training_data = pd.read_csv(training_data_path, compression="gzip", index_col=0)
training_data["Mitocheck_Phenotypic_Class"].value_counts()


# ### Only UMAP certain phenotypic classes

# In[3]:


classes_to_keep = [
    "Polylobed",
    "Binuclear",
    "Grape",
    "Interphase",
    "Prometaphase",
    "Artefact",
    "Apoptosis",
    # "ADCCM",
    # "MetaphaseAlignment",
    # "SmallIrregular",
    # "Hole",
    # "Large",
    # "Anaphase",
    # "Metaphase",
    # "UndefinedCondensed",
    # "Elongated",
    # "Folded",
]

training_data = training_data.loc[
    training_data["Mitocheck_Phenotypic_Class"].isin(classes_to_keep)
]
metadata_dataframe, feature_data = split_data(training_data)
phenotypic_classes = metadata_dataframe["Mitocheck_Phenotypic_Class"]

training_data


# ### Set UMAP display settings, save directory

# In[4]:


point_size = 25
alpha = 0.6
color_palette = "bright"

save_dir = pathlib.Path("umaps/")
save_dir.mkdir(exist_ok=True, parents=True)


# ### 1D UMAP

# In[5]:


umap_1D_save_path = pathlib.Path(f"{save_dir}/norm_train_1D_umap.png")
show_1D_umap(feature_data, phenotypic_classes, save_path=umap_1D_save_path, point_size=point_size, alpha=alpha, palette=color_palette)


# ### 2D UMAP

# In[6]:


umap_2D_save_path = pathlib.Path(f"{save_dir}/norm_train_2D_umap.png")
x_data, y_data = get_2D_umap_embeddings(feature_data)
show_2D_umap(x_data, y_data, phenotypic_classes, save_path=umap_2D_save_path, point_size=point_size, alpha=alpha, palette=color_palette)


# ### 3D UMAP

# In[7]:


umap_3D_save_path = pathlib.Path(f"{save_dir}/norm_train_3D_umap.png")
show_3D_umap(feature_data, phenotypic_classes, save_path=umap_3D_save_path, point_size=point_size, alpha=alpha, palette=color_palette)

