import pandas as pd
import pathlib
import re
import numpy as np

import warnings
from pandas.core.common import SettingWithCopyWarning


def get_frame_metadata(frame_details: str):
    """
    get frame metadata from features samples movie details string

    Parameters
    ----------
    frame_details : str
        string from one line of features samples file
        ex: PLLT0010_27--ex2005_05_13--sp2005_03_23--tt17--c5___P00173_01___T00082___X0397___Y0618

    Returns
    -------
    plate: str
        plate of sample
    well_num: int
        well number of sample
    frame: int
        frame of sample
    """

    plate = frame_details.split("--")[0].replace("PL", "")
    well_num = int(frame_details.split("___")[1][1:6])
    frame = int(frame_details.split("___")[2][1:6]) + 1

    return plate, well_num, frame


def get_uncompiled_training_locations(
    feature_samples_path: pathlib.Path, annotations_path: pathlib.Path
) -> pd.DataFrame:
    """
    get uncompiled training locations from features samples file
    has one entry per features samples file (may have repeated combinations of plate and well)

    Parameters
    ----------
    feature_samples_path : pathlib.Path
        path to features samples file
    annotations_path : pathlib.Path
        path to IDR study annotations file

    Returns
    -------
    pd.DataFrame
        dataframe with one entry per features samples file (may have repeats)
    """
    annotations = pd.read_csv(annotations_path, low_memory=False)
    # remove annotations for plates that are missing
    annotations = annotations.loc[annotations["Plate Issues"] != "plate missing"]
    training_data_locations = []

    with open(feature_samples_path) as labels_file:
        for line in labels_file:
            # get plate, well_num, and frame info from feature samples file line
            frame_details = line.strip().split("\t")[1]
            plate, well_num, frame = get_frame_metadata(frame_details)

            # get gene and well info from IDR study annotations file
            image_annotations = annotations.loc[
                (annotations["Plate"] == plate)
                & (annotations["Well Number"] == well_num)
            ]
            try:
                gene = image_annotations.iloc[0]["Original Gene Target"]
                # na gene corresponds to failed QC test (no gene is provided in annotations)
                # still useful for manually labeled individual cells, just means the whole well failed QC
                if pd.isna(gene):
                    gene = "failed QC"

                well = image_annotations.iloc[0]["Well"]
            except IndexError:
                # Some labeled data did not make it to IDR because of quality control issues
                print(f"Image from {plate}, {well_num} not in IDR")
                continue

            # compile frame details into pandas dataframe to append to all training data locations
            frame_details = {
                "Plate": plate,
                "Well": well,
                "Well Number": well_num,
                "Frames": frame,
                "Original Gene Target": gene,
            }

            training_data_locations.append(frame_details)

    return pd.DataFrame(training_data_locations)


def get_final_training_locations(
    uncompiled_training_locations: pd.DataFrame,
) -> pd.DataFrame:
    """
    removes repeated combinations of plate/well/frame

    Parameters
    ----------
    uncompiled_training_locations : pd.DataFrame
        dataframe with one entry per features samples file (may have repeats)

    Returns
    -------
    pd.DataFrame
        dataframe with one entry per plate/well/frames combo (does not have repeats)
    """
    # remove duplicate plate/well/frame combinations from cells in the same image
    final_training_locations = uncompiled_training_locations.drop_duplicates()
    final_training_locations = final_training_locations.reset_index(drop=True)

    # add columns necessary for idrstream_cp
    # plate map name is plate_wellNum
    final_training_locations["Plate_Map_Name"] = (
        final_training_locations["Plate"]
        + "_"
        + final_training_locations["Well Number"].astype(str)
    )
    # gene replicate and site always 1 for this data
    final_training_locations["Gene_Replicate"] = 1
    final_training_locations["Site"] = 1
    # DNA is path to DNA image after image is downloaded and saved with IDR_stream
    final_training_locations["DNA"] = (
        final_training_locations["Plate"]
        + "/"
        + final_training_locations["Plate"]
        + "_"
        + final_training_locations["Well Number"].astype(str)
        + "_"
        + final_training_locations["Frames"].astype(str)
        + ".tif"
    )

    return final_training_locations


def get_control_locations(
    annotations_path: pathlib.Path, control_type: str, numpy_seed: int
) -> pd.DataFrame:
    """
    get location data for mitocheck controls
    Parameters
    ----------
    annotations_path : pathlib.Path
        path to IDR curated annotations file
    control_type : str
        "negative" or "positive" depending on desired control type
    numpy_seed : int
        seed to use for np.random, ensures reproducibility
    Returns
    -------
    pd.DataFrame
        location data for controls
    """
    annotations = pd.read_csv(annotations_path, compression="gzip", dtype=object)
    # remove annotations for plates that are missing
    annotations = annotations.loc[
        annotations["Plate Issues"] != "plate missing"
    ]  # remove annotations for plates with irregular illumination
    annotations = annotations.loc[annotations["Well"] != "A1"]

    control_annotations = annotations.loc[annotations["Control Type"].notnull()]
    control_annotations = control_annotations.loc[
        control_annotations["Control Type"] != "empty well"
    ]
    control_annotations = control_annotations.loc[
        control_annotations["Control Type"].str.contains(control_type)
    ]

    # filter warning when setting with copy
    warnings.simplefilter(action="ignore", category=SettingWithCopyWarning)

    control_locations = control_annotations[
        ["Plate", "Well", "Well Number", "Original Gene Target"]
    ]
    # nan gene values correspond to negative control
    control_locations["Original Gene Target"] = control_locations[
        "Original Gene Target"
    ].fillna("negative control")

    # get random frame in middle third of mitosis movies (between frames 31 and 62)
    np.random.seed(numpy_seed)
    frames = np.random.randint(low=31, high=63, size=len(control_locations))
    control_locations["Frames"] = frames

    # add columns necessary for idrstream_cp
    # plate map name is plate_wellNum
    control_locations["Plate_Map_Name"] = (
        control_locations["Plate"] + "_" + control_locations["Well Number"]
    )
    # gene replicate and site always 1 for this data
    control_locations["Gene_Replicate"] = 1
    control_locations["Site"] = 1
    # DNA is path to DNA image after image is downloaded and saved with IDR_stream
    control_locations["DNA"] = (
        control_locations["Plate"]
        + "/"
        + control_locations["Plate"]
        + "_"
        + control_locations["Well Number"]
        + "_"
        + control_locations["Frames"].astype(str)
        + ".tif"
    )

    return control_locations.reset_index(drop=True)
