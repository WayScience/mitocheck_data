import pathlib
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from joblib import dump

import sys

sys.path.append("../utils")
from load_utils import compile_mitocheck_batch_data
from normalization_utils import get_normalization_scaler, get_normalized_mitocheck_data

# get normalization scaler from negative control features (normalization population)
print("Getting normalization scaler...")
negative_control_data_path = pathlib.Path(
    "../1.idr_streams/extracted_features__no_ic/negative_control_data/merged_features/"
)
normalization_scaler = get_normalization_scaler(negative_control_data_path)

# save normalization scaler
norm_scaler_save_path = pathlib.Path("scaler__no_ic/normalization_scaler.joblib")
norm_scaler_save_path.parent.mkdir(parents=True, exist_ok=True)
dump(normalization_scaler, norm_scaler_save_path)

# make results dir if it does not already exist
results_dir = pathlib.Path("normalized_data__no_ic/")
results_dir.mkdir(parents=True, exist_ok=True)

# normalize the data at the following paths
training_data_path = pathlib.Path(
    "../2.format_training_data/results__no_ic/training_data.csv.gz"
)
negative_control_data_path = pathlib.Path(
    "../1.idr_streams/extracted_features__no_ic/negative_control_data/merged_features/"
)
positive_control_data_path = pathlib.Path(
    "../1.idr_streams/extracted_features__no_ic/positive_control_data/merged_features/"
)

# normalize training data
print("Normalizing training data...")
data = pd.read_csv(training_data_path, compression="gzip", index_col=0)
normalized_data = get_normalized_mitocheck_data(data, normalization_scaler)
# save normalized training data
save_path = pathlib.Path(f"{results_dir}/{training_data_path.name}")
normalized_data.to_csv(save_path, compression="gzip")

# normalize negative control data
print("Loading negative control data...")
data = compile_mitocheck_batch_data(negative_control_data_path)
print("Normalizing negative control data...")
normalized_data = get_normalized_mitocheck_data(data, normalization_scaler)
# save normalized negative control data
save_path = pathlib.Path(f"{results_dir}/negative_control_data.csv.gz")
print("Saving normalized negative control data...")
normalized_data.to_csv(save_path, compression="gzip", index=False)

# normalize positive control data
print("Loading positive control data...")
data = compile_mitocheck_batch_data(positive_control_data_path)
print("Normalizing positive control data...")
normalized_data = get_normalized_mitocheck_data(data, normalization_scaler)
# save normalized positive control data
save_path = pathlib.Path(f"{results_dir}/positive_control_data.csv.gz")
print("Saving normalized positive control data...")
normalized_data.to_csv(save_path, compression="gzip", index=False)
