#!/bin/bash
# Go into streams/
cd streams/
# Make log folder if it does not already exist
mkdir -p logs
# Run all streams in streams/
for python_file in *.py; do python "$python_file"; done
