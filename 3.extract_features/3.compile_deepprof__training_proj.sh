#!/bin/bash
jupyter nbconvert --to python compile_deepprof_training_proj.ipynb
python compile_deepprof_training_proj.py
