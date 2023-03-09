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

training_data


# ### Set UMAP display settings, save directory, class colors

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
# in the second set of umaps
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


feature_types = ["CP", "DP", "CP_and_DP"]

for feature_type in feature_types:
    print(f"Showing UMAPs created with {feature_type} features")
    
    metadata_dataframe, feature_data = split_data(training_data, feature_type)
    phenotypic_classes = metadata_dataframe["Mitocheck_Phenotypic_Class"]
    
    # show 1D umaps
    # class colors 1 - all classes included
    show_1D_umap(feature_data, phenotypic_classes, class_colors_1, point_size=point_size, alpha=alpha)
    # class colors 2 - only certain classes included
    show_1D_umap(feature_data, phenotypic_classes, class_colors_2, point_size=point_size, alpha=alpha)
    
    # show 2D umaps
    # class colors 1 - all classes included
    show_2D_umap(feature_data, phenotypic_classes, class_colors_1, point_size=point_size, alpha=alpha)
    # class colors 2 - only certain classes included
    show_2D_umap(feature_data, phenotypic_classes, class_colors_2, point_size=point_size, alpha=alpha)

