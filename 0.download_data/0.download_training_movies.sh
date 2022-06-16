#!/bin/bash
jupyter nbconvert --to python aspera_training_downloader.ipynb
python aspera_training_downloader.py
