#!/bin/bash

# go into streams/
cd streams/

# activate conda environment for idrstream cp
conda activate idrstream_cp
# extract cp features
python cp_streams.py

# activate conda environment for idrstream dp
conda activate idrstream_dp
# extract cp features
python dp_streams.py

# merge features
python merge_streams.py
