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
                "Frame": frame,
                "Original Gene Target": gene,
            }

            training_data_locations.append(frame_details)

    return pd.DataFrame(training_data_locations)


def get_final_training_locations(
    uncompiled_training_locations: pd.DataFrame,
) -> pd.DataFrame:
    """
    compile individual training location entries into a final training locations dataframe with one entry per unique plate & well
    removes repeated combinations of plate and well

    Parameters
    ----------
    uncompiled_training_locations : pd.DataFrame
        dataframe with one entry per features samples file (may have repeats)

    Returns
    -------
    pd.DataFrame
        dataframe with one entry per plate and well combo (does not have repeats)
    """
    original_training_locations = uncompiled_training_locations
    final_training_locations = []

    # iterate through original training locations and compile all frames from same plate/well into one locations entry (with list of frames)
    # remove the particular plate/well locations from original training locations
    # contiue until original training locations is empty
    while not original_training_locations.empty:
        plate = original_training_locations.iloc[0]["Plate"]
        well_num = original_training_locations.iloc[0]["Well Number"]
        well = original_training_locations.iloc[0]["Well"]
        gene = original_training_locations.iloc[0]["Original Gene Target"]
        if pd.isna(gene):
            gene = "failed QC"

        plate_well_locations = original_training_locations.loc[
            (original_training_locations["Plate"] == plate)
            & (original_training_locations["Well Number"] == well_num)
        ]

        # compile all frames from the particular well and plate
        frames = []
        for frame in plate_well_locations["Frame"]:
            if frame not in frames:
                frames.append(frame)
        # convert frames to string for pandas dataframe
        frames_string = ",".join(map(str, frames))

        # add location details with entire frame string to final locations
        location_details = {
            "Plate": plate,
            "Well": well,
            "Well Number": well_num,
            "Frames": frames_string,
            "Original Gene Target": gene,
        }
        final_training_locations.append(location_details)

        # remove all locations corresponding to same plate, well
        original_training_locations = original_training_locations[
            ~original_training_locations.index.isin(plate_well_locations.index)
        ]

    final_training_locations = pd.DataFrame(final_training_locations)
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

    return control_locations.reset_index(drop=True)
