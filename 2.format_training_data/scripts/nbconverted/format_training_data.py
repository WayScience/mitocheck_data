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


# ## Set save directory

# In[2]:


results_dir = pathlib.Path("results/")
results_dir.mkdir(exist_ok=True, parents=True)


# ## Compile, Format, Save Training Data

# In[3]:


dataset_types = ["ic", "no_ic"]

for dataset_type in dataset_types:
    print(f"Compiling data for dataset type {dataset_type}")

    # Load training data
    training_data_features_path = pathlib.Path(f"../1.idr_streams/extracted_features/training_data__{dataset_type}/merged_features/")
    training_data = compile_mitocheck_batch_data(training_data_features_path)
    print(f"Training data has {training_data.shape}")
    
    # Find cells with MitoCheck data
    # Cells may not have feature data found because the specific well is not hosted on IDr (failure to pass QC) or because of differences in Mitocheck/DeepProfiler segmentation
    features_samples_path = pathlib.Path("../mitocheck_metadata/features.samples.txt")
    training_cells = get_labeled_cells(training_data, features_samples_path, "DP__Object_Outline")
    print(f"Shape of labeled_cells: {training_cells.shape}")
    
    # Replace `Shape1` and `Shape3` with their respective classes
    # See https://github.com/WayScience/mitocheck_data/issues/16 for more details
    training_cells = training_cells.replace("Shape1", "Binuclear")
    training_cells = training_cells.replace("Shape3", "Polylobed")
    
    # Save compiled training data
    compiled_training_data_path = pathlib.Path(f"{results_dir}/training_data__{dataset_type}.csv.gz")
    training_cells.to_csv(compiled_training_data_path, compression="gzip")

