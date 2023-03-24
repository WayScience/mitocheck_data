import pathlib
import pandas as pd
import numpy as np
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon


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
    center_x: int
        center x coord of cell
    center_y: int
        center y coord of cell
    """

    plate = frame_details.split("--")[0].replace("PL", "")
    well_num = int(frame_details.split("___")[1][1:6])
    frame = int(frame_details.split("___")[2][1:6]) + 1
    center_x = int(frame_details.split("___")[3][1:])
    center_y = int(frame_details.split("___")[4][1:])

    return plate, well_num, frame, center_x, center_y


def parse_outline_data(raw_outline_data: str) -> np.array:
    """
    parse outline data extracted with IDR stream into numpy array format

    Parameters
    ----------
    raw_outline_data : str
        string of outline data

    Returns
    -------
    np.array
        parsed outline data
    """
    outline_data = []

    raw_outline_data = raw_outline_data[1:-1]
    raw_outline_data = raw_outline_data.split("\n ")
    for coord_string in raw_outline_data:
        x = int(coord_string[1:-1].split()[0])
        y = int(coord_string[1:-1].split()[1])
        outline_data.append([x, y])

    return np.array(outline_data)


def center_in_outline(center_x: int, center_y: int, raw_outline_data: str) -> bool:
    """
    use shapely library to see if a point is in the raw outline data

    Parameters
    ----------
    center_x : int
        x coord of cell center
    center_y : int
        y coord of cell center
    raw_outline_data : str
        raw outline data of cell

    Returns
    -------
    bool
        whether or not coords are in outline
    """
    outline_data = parse_outline_data(raw_outline_data)
    point = Point(center_x, center_y)
    cell_polygon = Polygon(outline_data)
    return cell_polygon.contains(point)


def get_labeled_cells(
    training_data: pd.DataFrame,
    features_samples_path: pathlib.Path,
    outlines_column: str,
) -> pd.DataFrame:
    """
    get labeled cells as dataframe from all training data and features samples

    Parameters
    ----------
    training_data : pd.DataFrame
        all single cell features from all frames with any labeled cells
    features_samples_path : pathlib.Path
        path to features samples file
    outlines_column : str
        name of column in training_data that has outline data

    Returns
    -------
    pd.DataFrame
        dataframe with all labeled cells
    """
    with open(features_samples_path) as labels_file:
        labeled_cells = []

        # iterate through each sample and see if it has features in the total training data dataframe
        for line in labels_file:
            # get phenotpic label of cell from feature samples file line
            phenotypic_class = line.strip().split("\t")[0]
            # get frame info from feature samples file line
            frame_details = line.strip().split("\t")[1]
            plate, well_num, frame, center_x, center_y = get_frame_metadata(
                frame_details
            )
            # get all single cell features for this particular frame
            frame_cells = training_data.loc[
                (training_data["Metadata_Plate"] == plate)
                & (training_data["Metadata_Well"] == str(well_num))
                & (training_data["Metadata_Frame"] == str(frame))
            ]

            included = False
            # see if the center coords correspond to any feature data from the frame cells
            for _, row in frame_cells.iterrows():
                raw_outline_data = row[outlines_column]
                if center_in_outline(center_x, center_y, raw_outline_data):
                    full_row = pd.concat([pd.Series([phenotypic_class]), row])
                    labeled_cells.append(full_row)
                    included = True
                    break

            # some cells not found in DP-extracted feature collection because the wells are not hosted by IDR or differences in segmentation
            if not included:
                print(
                    f"No feature data derived for cell at: {plate}, {well_num}, {frame}, {center_x}, {center_y}"
                )

    labeled_cells = pd.DataFrame(labeled_cells)
    labeled_cells = labeled_cells.rename(
        columns={labeled_cells.columns[0]: "Mitocheck_Phenotypic_Class"}
    )
    # rename DP column that isnt part of features
    labeled_cells = labeled_cells.rename(
        columns={"DP__Object_Outline": "Metadata_Object_Outline"}
    )

    return labeled_cells
