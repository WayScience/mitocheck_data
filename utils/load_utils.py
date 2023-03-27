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
    # remove unecessary DP column that isnt part of features
    cols_to_load.remove("DP__Metadata_Model")

    # remove DP or CP features from columns to load depending on desired dataset
    if dataset == "CP":
        cols_to_load = [col for col in cols_to_load if "DP__" not in col]
    elif dataset == "DP":
        cols_to_load = [col for col in cols_to_load if "CP__" not in col]

    for batch_path in data_path.iterdir():
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
