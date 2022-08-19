#!/usr/bin/env python
# coding: utf-8

# ### Import libraries

# In[1]:


import pandas as pd
import pathlib
import re
import numpy as np

import sys
sys.path.append("../utils/")
from locate_utils import get_training_locations, get_control_locations


# ### Specify paths

# In[2]:


annotations_path = pathlib.Path("idr0013-screenA-annotation.csv.gz")
features_path = pathlib.Path("trainingset_2007_06_21.dat")

locations_dir = pathlib.Path("locations/")
locations_dir.mkdir(exist_ok=True, parents=True)


# ### Find/save training locations

# In[3]:


training_save_path = pathlib.Path(f"{locations_dir}/training_locations.tsv")

training_data_locations = get_training_locations(features_path, annotations_path)
training_data_locations.to_csv(training_save_path, sep="\t")

print(training_data_locations.shape)
training_data_locations.head()


# ### Find/save negative control locations

# In[4]:


negative_control_save_path = pathlib.Path(f"{locations_dir}/negative_control_locations.tsv")

negative_control_locations = get_control_locations(annotations_path, "negative", 0)
negative_control_locations.to_csv(negative_control_save_path, sep="\t")

print(negative_control_locations.shape)
negative_control_locations.head()


# ### Find/save positive control locations

# In[5]:


positive_control_save_path = pathlib.Path(f"{locations_dir}/positive_control_locations.tsv")

positive_control_locations = get_control_locations(annotations_path, "positive", 1)
positive_control_locations.to_csv(positive_control_save_path, sep="\t")

print(positive_control_locations.shape)
positive_control_locations.head()

