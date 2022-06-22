#!/bin/bash
jupyter nbconvert --to python segment_training_data.ipynb
python segment_training_data.py
