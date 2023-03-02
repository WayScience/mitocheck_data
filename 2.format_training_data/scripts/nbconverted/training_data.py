#!/usr/bin/env python
# coding: utf-8

# ### Import libraries

# In[1]:


import pathlib
import pandas as pd
import numpy as np

import sys
sys.path.append("../utils")
from load_utils import compile_mitocheck_batch_data
from training_data_utils import get_labeled_cells


# ### Compile training data batches into one dataframe

# In[2]:


training_data_features_path = pathlib.Path("../1.idr_streams/extracted_features/training_data/merged_features/")
training_data = compile_mitocheck_batch_data(training_data_features_path)
print(training_data.shape)
training_data.head()


# ### Find cells with Mitocheck-assigned labels
# 
# #### Cells may not have feature data found because the specific well is not hosted on IDr (failure to pass QC) or because of differences in Mitocheck/DeepProfiler segmentation

# In[3]:


features_samples_path = pathlib.Path("../mitocheck_metadata/features.samples.txt")

labeled_cells = get_labeled_cells(training_data, features_samples_path, "DP__Object_Outline")  
print(f"Shape of labeled_cells: {labeled_cells.shape}")


# ### Replace `Shape1` and `Shape3` with their respective classes
# #### See [#16](https://github.com/WayScience/mitocheck_data/issues/16) for more details

# In[4]:


labeled_cells = labeled_cells.replace("Shape1", "Binuclear")
labeled_cells = labeled_cells.replace("Shape3", "Polylobed")


# ### Preview labeled cells

# In[5]:


labeled_cells


# ### Save labeled training data

# In[6]:


results_dir = pathlib.Path("results/")
results_dir.mkdir(exist_ok=True, parents=True)

compiled_training_data_path = pathlib.Path(f"{results_dir}/training_data.csv.gz")
labeled_cells.to_csv(compiled_training_data_path, compression="gzip")

