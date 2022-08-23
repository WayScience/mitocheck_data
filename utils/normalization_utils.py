import pathlib
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

from load_utils import compile_mitocheck_batch_data, split_data


def get_normalization_scaler(norm_pop_path: pathlib.Path) -> StandardScaler():
    """
    get normalization scaler from a normalization population

    Parameters
    ----------
    norm_pop_path : pathlib.Path
        path to normalization output in form of mitocheck IDR stream output

    Returns
    -------
    StandardScaler
        scaler to be used for data normalization
    """
    # get normalization population
    norm_pop_data = compile_mitocheck_batch_data(norm_pop_path)

    # derive normalization scaler
    _, norm_pop_feature_data = split_data(norm_pop_data)
    scaler = StandardScaler()
    scaler.fit(norm_pop_feature_data)

    return scaler


def get_normalized_mitocheck_data(
    data: pd.DataFrame, scaler: StandardScaler()
) -> pd.DataFrame:
    """
    get normalized version of mitocheck data

    Parameters
    ----------
    data : pd.DataFrame
        data to be normalized, in form of compiled mitocheck IDR output
    scaler : StandardScaler
        scaler to use for data normalization

    Returns
    -------
    pd.DataFrame
        normalized data
    """

    # normalize features from data
    col_list = data.columns.tolist()
    derived_features = [col_name for col_name in col_list if "efficientnet" in col_name]
    features = data[derived_features].to_numpy()
    features = scaler.transform(features)
    # make features a dataframe so it can be combined with metadata
    features = pd.DataFrame(features, columns=derived_features)

    # replace original features of data with normalized features
    metadata = [col_name for col_name in col_list if "efficientnet" not in col_name]
    metadata = data[metadata]

    return pd.concat([metadata, features], axis=1)
