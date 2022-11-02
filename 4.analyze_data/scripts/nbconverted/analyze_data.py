#!/usr/bin/env python
# coding: utf-8

# ### Import libraries

# In[1]:


import pathlib
import pandas as pd
import seaborn as sns
from matplotlib.colors import rgb2hex

import sys
sys.path.append("../utils")
from load_utils import split_data
from analysis_utils import get_class_colors, show_1D_umap, show_2D_umap, show_3D_umap


# ### Load training data

# In[2]:


training_data_path = pathlib.Path("../3.normalize_data/normalized_data/training_data.csv.gz")
training_data = pd.read_csv(training_data_path, compression="gzip", index_col=0)

metadata_dataframe, feature_data = split_data(training_data)
phenotypic_classes = metadata_dataframe["Mitocheck_Phenotypic_Class"]

training_data


# ### Set UMAP display settings, save directory

# In[3]:


point_size = 25
alpha = 0.6
color_palette = "bright"

save_dir = pathlib.Path("umaps/")
save_dir.mkdir(exist_ok=True, parents=True)


# ### Set class colors

# In[4]:


training_data["Mitocheck_Phenotypic_Class"].unique().tolist()


# In[5]:


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

class_colors_2


# ### 1D UMAP

# In[6]:


umap_1D_save_path = pathlib.Path(f"{save_dir}/norm_train_1D_umap.png")
show_1D_umap(feature_data, phenotypic_classes, class_colors_1, save_path=umap_1D_save_path, point_size=point_size, alpha=alpha)


# In[7]:


umap_1D_save_path = pathlib.Path(f"{save_dir}/norm_train_1D_umap_other.png")
show_1D_umap(feature_data, phenotypic_classes, class_colors_2, save_path=umap_1D_save_path, point_size=point_size, alpha=alpha)


# ### 2D UMAP

# In[8]:


umap_2D_save_path = pathlib.Path(f"{save_dir}/norm_train_2D_umap.png")
show_2D_umap(feature_data, phenotypic_classes, class_colors_1, save_path=umap_2D_save_path, point_size=point_size, alpha=alpha)


# In[9]:


umap_2D_save_path = pathlib.Path(f"{save_dir}/norm_train_2D_umap_other.png")
show_2D_umap(feature_data, phenotypic_classes, class_colors_2, save_path=umap_2D_save_path, point_size=point_size, alpha=alpha)


# ### 3D UMAP

# In[10]:


umap_3D_save_path = pathlib.Path(f"{save_dir}/norm_train_3D_umap.png")
show_3D_umap(feature_data, phenotypic_classes, class_colors_1, save_path=umap_3D_save_path, point_size=point_size, alpha=alpha)


# In[11]:


umap_3D_save_path = pathlib.Path(f"{save_dir}/norm_train_3D_umap_other.png")
show_3D_umap(feature_data, phenotypic_classes, class_colors_2, save_path=umap_3D_save_path, point_size=point_size, alpha=alpha)

