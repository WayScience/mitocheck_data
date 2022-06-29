#!/usr/bin/env python
# coding: utf-8

# # Use PyCytominer to normalize single cell data from DeepProfiler run
# 
# ### Import libraries 

# In[1]:


import pathlib
from pycytominer.cyto_utils import DeepProfiler_processing
import pandas as pd


# ### PyCytominer normalization

# In[2]:


index_file = pathlib.Path("../3.extract_features/inputs/metadata/index.csv")
profile_dir = pathlib.Path("../3.extract_features/outputs/efn_pretrained/features")
output_dir = pathlib.Path("data/")

deep_data = DeepProfiler_processing.DeepProfilerData(index_file, profile_dir, filename_delimiter="/")
deep_single_cell = DeepProfiler_processing.SingleCellDeepProfiler(deep_data)
output_dir.mkdir(parents=True, exist_ok=True)
normalized = deep_single_cell.normalize_deep_single_cells(
    image_features=False, # profiles contain DeepProfiler features, not image features
    samples="all", # normalize all samples
    method="standardize", # use sklearn StandardScaler to standardize features
    output_file=f"{output_dir}/normalized_training_data.csv.gz",
    compression_options={"method": "gzip", "mtime": 1}
    )


# In[3]:


print(normalized.shape)


# In[4]:


print(normalized.head())

