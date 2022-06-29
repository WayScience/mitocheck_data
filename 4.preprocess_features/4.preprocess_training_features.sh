#!/bin/bash
jupyter nbconvert --to python 4.preprocess_training_features.ipynb
python 4.preprocess_training_features.py
