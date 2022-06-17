#!/bin/bash
jupyter nbconvert --to python preprocess_training_data.ipynb
python preprocess_training_data.py