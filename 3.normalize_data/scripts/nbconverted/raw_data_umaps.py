#!/usr/bin/env python
# coding: utf-8

# ### Import libraries

# In[1]:


import pathlib
import sys

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

sys.path.append("../utils")
from load_utils import compile_mitocheck_batch_data, split_data
from analysis_utils import get_2D_umap_embeddings, show_2D_umap_from_embeddings


# ### Compile control data

# ### Set features load path, dataset/feature types, meatadata fields

# In[2]:


extracted_features_path = pathlib.Path(f"../1.idr_streams/extracted_features/")

dataset_types = ["ic", "no_ic"]
feature_types = ["CP", "DP", "CP_and_DP"]
metadata_fields = ["Metadata_Plate", "Metadata_Well", "Metadata_Frame", "Metadata_Gene"]


# ### Get control data, get umap embeddings, create umap

# In[3]:


for dataset_type in dataset_types:
    
    # compile a fraction of control data
    print(f"Compiling control data for dataset type {dataset_type}...")
    
    # get 10% of negative control features
    negative_control_data_path = pathlib.Path(f"{extracted_features_path}/negative_control_data__{dataset_type}/merged_features")
    negative_control_data = compile_mitocheck_batch_data(negative_control_data_path)
    negative_control_data = negative_control_data.sample(frac=0.1, random_state=0)

    # get 10% of positive control features
    positive_control_data_path = pathlib.Path(f"{extracted_features_path}/positive_control_data__{dataset_type}/merged_features")
    positive_control_data = compile_mitocheck_batch_data(positive_control_data_path)
    positive_control_data = positive_control_data.sample(frac=0.1, random_state=0)

    # combine negative and positive control features
    control_data = pd.concat([negative_control_data, positive_control_data])
    # shuffle data so negative/positive controls are not ordered
    control_data = control_data.sample(frac=1, random_state=0)
    
    # get 2D umap embeddings
    for feature_type in feature_types:
        print(f"Getting 2D umap embeddings for feature type {feature_type}...")
        metadata_dataframe, feature_data = split_data(control_data, feature_type)
        x_data, y_data = get_2D_umap_embeddings(feature_data)
        
        # create 2D umaps colored by metadata
        for metadata_field in metadata_fields:
            print(f"Creating 2D umap for metadata field {metadata_field}...")
            metadata = metadata_dataframe[metadata_field]
            show_2D_umap_from_embeddings(x_data, y_data, metadata)

