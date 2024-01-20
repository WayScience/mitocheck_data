import pathlib
import sys
import itertools

import pandas as pd

sys.path.append("../IDR_stream/")
from idrstream.merge_CP_DP import save_merged_CP_DP_run

# path to directory with IDR_stream run outputs (training_data, negative_control_data, positive_control_data)
extracted_features = pathlib.Path("../extracted_features/")

data_types = ["negative_control_data", "positive_control_data", "training_data"]
dataset_types = ["ic", "no_ic"]

for data_type, dataset_type in itertools.product(data_types, dataset_types):
    print(f"Merging streams for data type {data_type} and dataset type {dataset_type}")
    
    base_dir_path = pathlib.Path(f"{extracted_features}/{data_type}__{dataset_type}/")
    print(base_dir_path)

    # specify paths to CP, DP and merged data
    cp_data_dir_path = pathlib.Path(f"{base_dir_path}/CP_features")
    dp_data_dir_path = pathlib.Path(f"{base_dir_path}/CP_features")
    merged_data_dir_path = pathlib.Path(f"{base_dir_path}/merged_features")

    # merge CP and DP runs!
    save_merged_CP_DP_run(cp_data_dir_path, dp_data_dir_path, merged_data_dir_path)
