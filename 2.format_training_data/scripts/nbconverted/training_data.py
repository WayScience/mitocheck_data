#!/usr/bin/env python
# coding: utf-8

# ### Import libraries

# In[1]:


import pathlib
import pandas as pd

import sys
sys.path.append("../utils")
from load_utils import compile_mitocheck_batch_data
from training_data_utils import get_labeled_cells


# ### Compile training data batches into one dataframe

# In[2]:


training_data_features_path = pathlib.Path("../1.idr_streams/extracted_features/training_data")
training_data = compile_mitocheck_batch_data(training_data_features_path)
training_data


# ### Find cells with Mitocheck-assigned labels

# In[3]:


features_path = pathlib.Path("../mitocheck_metadata/features/")
training_set_dat_path = pathlib.Path("../mitocheck_metadata/trainingset_2007_06_21.dat")

labeled_cells = get_labeled_cells(features_path, training_set_dat_path, training_data)
labeled_cells


# ### Save labeled training data

# In[4]:


results_dir = pathlib.Path("results/")
results_dir.mkdir(exist_ok=True, parents=True)

compiled_training_data_path = pathlib.Path(f"{results_dir}/training_data.csv.gz")
labeled_cells.to_csv(compiled_training_data_path, compression="gzip")

