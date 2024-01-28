import pathlib
import pandas as pd


def compile_mitocheck_batch_data(
    data_path: pathlib.Path, dataset: str = "CP_and_DP"
) -> pd.DataFrame:
    """
    compile batch data from a mitocheck idrstream merged features run

    Parameters
    ----------
    data_path : pathlib.Path
        path to folder with saved batches
        these batches must be merged (have CP and DP features)
    dataset : str, optional
        which dataset columns to load in (in addition to metadata),
        can be "CP" or "DP" or by default "CP_and_DP"

    Returns
    -------
    pd.DataFrame
        compiled batch dataframe
    """

    data = pd.DataFrame()

    # determine which cols to use for loading (depending on dataset)
    # load in first row to get all column names
    batch_0_row_0 = pd.read_csv(
        f"{data_path}/batch_0.csv.gz",
        compression="gzip",
        index_col=0,
        low_memory=False,
        nrows=1,
    )
    cols_to_load = batch_0_row_0.columns.to_list()
    print(cols_to_load)

    # remove unecessary DP column that isnt part of features
    cols_to_remove = ["DP__Metadata_Model"]

    # Some CP columns are related to things besides the features we want (ex. location measurements)
    # We only want to get CP data from the feature modules below (__ ensures it is found as module name)
    cp_feature_modules = ["__AreaShape_", "__Granularity_", "__Intensity", "__Neighbors", "__RadialDistribution", "__Texture"]
    # remove CP columns that dont have a feature module as a substring
    for col in cols_to_load:
        if "CP__" not in col:
            continue
        has_feature_module = any(feature_module in col for feature_module in cp_feature_modules)
        if not has_feature_module:
            cols_to_remove.append(col)
    
    # remove columns we don't want from the list to load
    cols_to_load = list(set(cols_to_load) - set(cols_to_remove))

    # remove DP or CP features from columns to load depending on desired dataset
    if dataset == "CP":
        cols_to_load = [col for col in cols_to_load if "DP__" not in col]
    if dataset == "DP":
        cols_to_load = [col for col in cols_to_load if "CP__" not in col]

    print(f"Loading data from {data_path}...")
    for batch_path in data_path.iterdir():
        print(f"Loading batch data from {batch_path}...")
        batch = pd.read_csv(
            batch_path,
            compression="gzip",
            low_memory=True,
            usecols=cols_to_load,
        )

        # split well_frame into well and frame columns
        batch[["Metadata_Well", "Metadata_Frame"]] = batch["Metadata_Well"].str.split(
            "_", expand=True
        )
        batch.insert(5, "Metadata_Frame", batch.pop("Metadata_Frame"))

        if data.empty:
            data = batch
        else:
            data = pd.concat([data, batch])

    return data.reset_index(drop=True)


def split_data(pycytominer_output: pd.DataFrame, dataset: str = "CP_and_DP"):
    """
    split pycytominer output to metadata dataframe and np array of feature values

    Parameters
    ----------
    pycytominer_output : pd.DataFrame
        dataframe with pycytominer output
    dataset : str, optional
        which dataset features to split,
        can be "CP" or "DP" or by default "CP_and_DP"

    Returns
    -------
    pd.Dataframe, np.ndarray
        metadata dataframe, feature values
    """
    all_cols = pycytominer_output.columns.tolist()

    # get DP,CP, or both features from all columns depending on desired dataset
    if dataset == "CP":
        feature_cols = [col for col in all_cols if "CP__" in col]
    elif dataset == "DP":
        feature_cols = [col for col in all_cols if "DP__" in col]
    elif dataset == "CP_and_DP":
        feature_cols = [col for col in all_cols if "P__" in col]

    # metadata columns is all columns except feature columns
    metadata_cols = [col for col in all_cols if "P__" not in col]

    metadata_dataframe = pycytominer_output[metadata_cols]
    feature_data = pycytominer_output[feature_cols].values

    return metadata_dataframe, feature_data
