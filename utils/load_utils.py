import pathlib
import pandas as pd

def compile_mitocheck_batch_data(data_path: pathlib.Path) -> pd.DataFrame:
    """
    compile batch data from a mitocheck idrstream run

    Parameters
    ----------
    data_path : pathlib.Path
        path to folder with saved batches

    Returns
    -------
    pd.DataFrame
        compiled batch dataframe
    """
    data = pd.DataFrame()
    
    for batch_path in data_path.iterdir():
        batch = pd.read_csv(batch_path, compression="gzip", index_col=0, low_memory=False)
        
        # split well_frame into well and frame columns
        batch[["Metadata_Well", "Metadata_Frame"]] = batch["Metadata_Well"].str.split("_",expand=True)
        batch.insert(4, "Metadata_Frame", batch.pop("Metadata_Frame"))
        
        if data.empty:
            data = batch
        else:
            data = pd.concat([data, batch])
        
    return data.reset_index(drop=True)

def split_data(pycytominer_output: pd.DataFrame):
    # split metadata from features
    metadata_cols = [
        col_name
        for col_name in pycytominer_output.columns.tolist()
        if "efficientnet" not in col_name
    ]
    metadata_dataframe = pycytominer_output[metadata_cols]

    feature_cols = [
        col_name
        for col_name in pycytominer_output.columns.tolist()
        if "efficientnet" in col_name
    ]
    feature_data = pycytominer_output[feature_cols].values

    return metadata_dataframe, feature_data
