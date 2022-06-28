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


index_file = pathlib.Path("/home/roshankern/Desktop/Github/mitocheck_data/3.extract_features/inputs/metadata/index.csv")
profile_dir = pathlib.Path("/home/roshankern/Desktop/Github/mitocheck_data/3.extract_features/outputs/efn_pretrained/features")

deep_data = DeepProfiler_processing.DeepProfilerData(index_file, profile_dir, filename_delimiter="/")
deep_single_cell = DeepProfiler_processing.SingleCellDeepProfiler(deep_data)
deep_single_cell.normalize_deep_single_cells(output_file="normalized_training_data.csv")

