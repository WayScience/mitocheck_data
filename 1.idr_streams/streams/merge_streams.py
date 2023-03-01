import pandas as pd
import pathlib

import sys
sys.path.append("../IDR_stream/")
from idrstream.merge_CP_DP import save_merged_CP_DP_run

# path to directory with IDR_stream run outputs (training_data, negative_control_data, positive_control_data)
extracted_features = pathlib.Path("../extracted_features/")

for extracted_features_dir in sorted(extracted_features.iterdir()):
    print(f"Merging streams for {extracted_features_dir.name}")
    
    # specify paths to CP, DP and merged data
    cp_data_dir_path = pathlib.Path(f"{extracted_features_dir}/CP_features/")
    dp_data_dir_path = pathlib.Path(f"{extracted_features_dir}/DP_features/")
    merged_data_dir_path = pathlib.Path(f"{extracted_features_dir}/merged_features/")

    # merge CP and DP runs!
    save_merged_CP_DP_run(cp_data_dir_path, dp_data_dir_path, merged_data_dir_path)