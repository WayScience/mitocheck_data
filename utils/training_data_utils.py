import pathlib
import pandas as pd

def get_frame_features_path(features_path, plate, well, frame):
    well_string = str(well).zfill(3)
    movie_path = pathlib.Path(f"{features_path}/{plate}/features/{well_string}/")
    frame_time = (int(frame)-1)*30
    frame_time_string = f"T{str(frame_time).zfill(5)}"
    
    for frame_file in movie_path.iterdir():
        if(frame_time_string in frame_file.name):
            return frame_file

def get_frame_labels(training_set_dat_path, plate, well, frame):
    well_string = f"W{str(well).zfill(5)}"
    frame_time = (int(frame)-1)*30
    frame_time_string = f"T{str(frame_time).zfill(5)}"
    frame_file_details = [plate, well_string, frame_time_string]
    
    frame_objects = []
    with open(training_set_dat_path) as trainingset_file:
        append = False
        for line in trainingset_file:
            if append and ".tif" in line:
                append = False
            if append:
                object_details = line.strip().split(": ")
                frame_objects.append(object_details)
            #match plate, well, frame to file name
            if all(detail in line for detail in frame_file_details):
                append = True
    return frame_objects

def is_labeled(centroid, frame_features, frame_labels):
    """
    returns true if nucleus is included in labeled training data, false if not
    """
    objID = -1
    labeled = False
    
    #determine if centroid is inside any of labeled bounding boxes
    x = centroid[0]
    y = centroid[1]
    for labels in frame_labels:
        labeled_feature = frame_features[frame_features[0] == int(labels[0])]
        upperLeft_x = labeled_feature.iloc[0][1]
        upperLeft_y = labeled_feature.iloc[0][2]
        width = labeled_feature.iloc[0][3]
        height = labeled_feature.iloc[0][4]
        bottomRight_x = upperLeft_x + width
        bottomRight_y = upperLeft_y + height
        if upperLeft_x <= x and x <= bottomRight_x:
            if y >= upperLeft_y and y <= bottomRight_y:
                objID = labeled_feature.iloc[0][0]
                labeled = True
        
    return objID, labeled

def get_cell_class(
    training_set_dat_path: pathlib.Path,
    plate: str,
    well: int,
    frame: str,
    obj_id: int,
) -> str:
    """get phenotypic class of cell from trainingset.dat file, as labeled by Mitocheck

    Args:
        single_cell_data (pd.DataFrame): dataframe with single cell data
        trainingset_file_url (str): url location of raw traininset.dat file
        plate (str): plate cell is from
        well (str): well cell is from
        frame (str): frame cell is from

    Returns:
        str: phenotypic class of nucleus, as labeled by MitoCheck
    """
    well_string = f"W{str(well).zfill(5)}"
    frame_time = (int(frame) - 1) * 30
    frame_time_string = f"T{str(frame_time).zfill(5)}"
    frame_file_details = [plate, well_string, frame_time_string]
    obj_id_prefix = f"{obj_id}: "

    append = False
    # need to open trainingset file each time
    with open(training_set_dat_path) as trainingset_file:
        for line in trainingset_file:
            decoded_line = line.strip()
            # match plate, well, frame to starting line for movie labels
            if all(detail in decoded_line for detail in frame_file_details):
                append = True
            if append and decoded_line.startswith(obj_id_prefix):
                return decoded_line.split(": ")[1]
    return None

def get_labeled_cells(features_path: pathlib.Path, training_set_dat_path: pathlib.Path, training_data: pd.DataFrame) -> pd.DataFrame:
    labeled_cells = []

    for index, row in training_data.iterrows():
        centroid = (row["Location_Center_X"], row["Location_Center_Y"])
        plate = row["Metadata_Plate"]
        well = row["Metadata_Well"]
        frame = row["Metadata_Frame"]
        try:
            frame_features_path = get_frame_features_path(
                features_path, plate, well, frame
            )
            frame_features = pd.read_csv(
                frame_features_path, compression="gzip", header=None
            )
            frame_labels = get_frame_labels(training_set_dat_path, plate, well, frame)
            obj_id, cell_is_labeled = is_labeled(centroid, frame_features, frame_labels)
            obj_id = int(obj_id)

            if cell_is_labeled:
                phenotypic_class = get_cell_class(
                    training_set_dat_path, plate, well, frame, obj_id
                )

                additional_metadata = pd.Series({
                    "Mitocheck_Phenotypic_Class": phenotypic_class,
                    "Mitocheck_Object_ID": obj_id,
                })
                cell_data = pd.concat([additional_metadata, row])
                labeled_cells.append(cell_data)
        except IndexError as e:
            print(
                f"Cell at: {plate}, {well}, {frame}, location: {centroid} not found in features dataset"
            )

    return pd.DataFrame(labeled_cells)