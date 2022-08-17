import pandas as pd
import pathlib
import re
import numpy as np

def find_training_frames(trainingset_path, training_plate, training_well_num) -> list:
    frames = []

    with open(trainingset_path) as labels_file:
        for line in labels_file:
            if ".tif" in line:  # look at lines with plates/wells
                image_details = line.split("--")
                plate = image_details[0]
                well_num = int(image_details[1].replace("W0", ""))
                # time of frame in minutes (frames captured 30 min apart)
                time = int(image_details[3].replace("T", ""))
                frame = int(time / 30 + 1)

                if plate == training_plate and well_num == training_well_num:
                    frames.append(str(frame))

    return frames


# Read plates listed in features dataset to figure out which wells from which plates have labeled data
# Save these training locations into a file
def get_training_locations(trainingset_path, annotations_path):
    annotations = pd.read_csv(annotations_path, low_memory=False)
    # remove annotations for plates that are missing
    annotations = annotations.loc[annotations["Plate Issues"] != "plate missing"]
    training_data_locations = pd.DataFrame()

    with open(trainingset_path) as labels_file:
        for line in labels_file:
            if ".tif" in line:  # look at lines with plates/wells
                image_details = line.split("--")
                plate = image_details[0]
                well_num = int(image_details[1].replace("W0", ""))
                # time of frame in minutes (frames captured 30 min apart)
                time = int(image_details[3].replace("T", ""))
                frame = int(time / 30 + 1)

                frames = find_training_frames(trainingset_path, plate, well_num)
                frames = ",".join(frames)
                image_annotations = annotations.loc[
                    (plate == annotations["Plate"])
                    & (annotations["Well Number"] == well_num)
                ]
                try:
                    gene = image_annotations.iloc[0]["Original Gene Target"]
                    well = image_annotations.iloc[0]["Well"]
                except IndexError:
                    print(f"Image from {plate}, {well_num} not in IDR")
                    continue

                frame_details = pd.DataFrame(
                    {
                        "Plate": [plate],
                        "Well": [well],
                        "Well Number": [well_num],
                        "Frames": [frames],
                        "Original Gene Target": [gene],
                    }
                )

                if training_data_locations.empty:
                    training_data_locations = frame_details
                else:
                    # see if this well has already been added to training data
                    if not (
                        plate in training_data_locations["Plate"].unique()
                        and well_num in training_data_locations["Well Number"].unique()
                    ):
                        training_data_locations = pd.concat([training_data_locations, frame_details])

    # nan gene values correspond to negative control
    training_data_locations["Original Gene Target"] = training_data_locations[
        "Original Gene Target"
    ].replace(np.NaN, "negative control")
    return training_data_locations

def get_control_locations(
    annotations_path: pathlib.Path, control_type: str = "negative"
):
    annotations = pd.read_csv(annotations_path, compression="gzip", dtype=object)
    # remove annotations for plates that are missing
    annotations = annotations.loc[annotations["Plate Issues"] != "plate missing"]\
    # remove annotations for plates with irregular illumination
    annotations = annotations.loc[annotations["Well"] != "A1"]

    control_annotations = annotations.loc[annotations["Control Type"].notnull()]
    control_annotations = control_annotations.loc[
        control_annotations["Control Type"] != "empty well"
    ]
    control_annotations = control_annotations.loc[
        control_annotations["Control Type"].str.contains(control_type)
    ]

    control_locations = control_annotations[
        ["Plate", "Well", "Well Number", "Original Gene Target"]
    ]
    control_locations["Original Gene Target"] = control_locations[
        "Original Gene Target"
    ].fillna("negative control")
    
    # get random frame in middle third of mitosis movies (between frames 31 and 62)
    np.random.seed(0)
    frames = np.random.randint(low=31, high=63, size=len(control_locations))
    control_locations["Frames"] = frames

    return control_locations