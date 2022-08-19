#!/bin/bash
# Convert notebook to python file and execute
jupyter nbconvert --to python \
        --FilesWriter.build_directory=scripts/nbconverted \
        --execute locate_data.ipynb
