#!/bin/bash
# Go into streams/
cd streams/
# Run all streams in streams/
for python_file in *.py; do python "$python_file"; done
