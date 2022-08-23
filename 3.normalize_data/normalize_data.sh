#!/bin/bash
# Convert umap notebook to python file and execute
jupyter nbconvert --to python \
        --FilesWriter.build_directory=scripts/nbconverted \
        --execute raw_data_maps.ipynb
# Normalize data
python normalize_data.py