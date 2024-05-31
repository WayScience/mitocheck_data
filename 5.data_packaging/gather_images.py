"""
Python module for gathering images from Image Data Resource (IDR).
"""

import os
import pathlib
from ftplib import FTP
from typing import List

import awkward as ak
import docker
import duckdb
import pyarrow as pa
import tifffile
from constants import (
    DOCKER_PLATFORM,
    FTP_IDR_MITOCHECK_CH5_DIR,
    FTP_IDR_URL,
    FTP_IDR_USER,
)
import numpy as np
import pyarrow.compute as pc
import h5py
from pyarrow import parquet


def retrieve_ftp_file(
    ftp_file: str,
    download_dir: str,
    ftp_url: str = FTP_IDR_URL,
    ftp_user: str = FTP_IDR_USER,
    ftp_pass: str = "",
) -> str:
    """
    Retrieve a file using FTP.

    Args:
        ftp_file (str):
            The name of the file to retrieve.
        download_dir (str):
            The directory where the file will be downloaded.
        ftp_url (str, optional):
            The URL of the FTP server. Defaults to FTP_IDR_URL.
        ftp_user (str, optional):
            The username for accessing the FTP server. Defaults to FTP_IDR_USER.
        ftp_pass (str, optional):
            The password for accessing the FTP server. Defaults to "".

    Returns:
        str:
            A string indicating the path to the downloaded file.
    """

    # Specify the file to download
    download_filepath = f"{download_dir}/{pathlib.Path(ftp_file).name}"

    # if we already have the file, avoid a re-download by returning early
    if pathlib.Path(download_filepath).is_file():
        return download_filepath

    try:
        # Connect to the FTP server
        with FTP(ftp_url) as ftp:
            # Log in to the FTP server
            ftp.login(user=ftp_user, passwd=ftp_pass)

            # Open a local file for writing in binary mode
            with open(download_filepath, "wb") as local_file:
                # Download the file from the FTP server
                ftp.retrbinary(f"RETR {ftp_file}", local_file.write)

        # return the download filepath
        return download_filepath

    except Exception as e:
        print("An error occurred:", e)


def get_image_union_table() -> pa.Table:
    """
    Build a table with relevant information to extract images.

    Returns:
        pa.Table:
            A PyArrow table containing relevant information for image extraction.
    """

    with duckdb.connect() as ddb:
        return ddb.execute(
            f"""
            /* concat all locations data together as a single table */
            WITH locations_union AS (
                SELECT *
                FROM read_csv('0.locate_data/locations/negative_control_locations.tsv')
                UNION ALL
                SELECT *
                FROM read_csv('0.locate_data/locations/positive_control_locations.tsv')
                UNION ALL
                SELECT *
                FROM read_csv('0.locate_data/locations/training_locations.tsv')
            )
            /* join locations with additional plate location data */
            SELECT
                locations_union.*,
                /* create a dotted notation filename for extracting image frames from ch5 files */
                replace(locations_union.DNA, '/', '.') AS DNA_dotted_notation,
                /* clean up screen location string for IDR FTP location work below */
                replace(
                    replace(plates.Screen, '../screens/', ''),
                    '.screen',
                    ''
                    ) AS Screen_cleaned,
                /* build an IDR path from other data based on IDR_Stream:
                https://github.com/WayScience/IDR_stream/blob/main/idrstream/download.py#L95 */
                concat(
                    '{FTP_IDR_MITOCHECK_CH5_DIR}',
                    '/',
                    Screen_cleaned,
                    '/hdf5/00',
                    format('{{:03d}}', locations_union."Well Number"),
                    '_01.ch5'
                ) AS IDR_FTP_ch5_location,
                'TARGET_FRAME' as Frame_type
            FROM locations_union
            LEFT JOIN read_csv('1.idr_streams/stream_files/idr0013-screenA-plates-w-colnames.tsv') as plates ON
                    plates.Plate = locations_union.Plate
            LIMIT 1;
            """
        ).arrow()


def run_dockerfile_container(
    dockerfile: str,
    image_name: str,
    volumes: List[str],
    command: str,
) -> None:
    """
    Build, run, and stream logs from a Dockerfile-based container.

    Args:
        dockerfile (str):
            The path to the Dockerfile.
        image_name (str):
            The name of the Docker image to build.
        volumes (List[str]):
            List of volume mounts for the container.
        command (str):
            The command to execute inside the container.

    Returns:
        None
    """

    print(
        f"Running Docker container {image_name} based on {dockerfile} with command '{command}'."
    )

    # Initialize the Docker client
    client = docker.from_env()

    # Build the Docker image using the Dockerfile
    client.images.build(
        path=str(pathlib.Path(dockerfile).parent),
        dockerfile=pathlib.Path(dockerfile).name,
        tag=image_name,
        platform=DOCKER_PLATFORM,
    )

    # Run a container based on the built image, mounting a local directory
    container = client.containers.run(
        image=image_name,
        volumes=volumes,
        command=command,
        remove=True,
        detach=True,
    )

    # capture log messages from detached container
    process = container.logs(stream=True, follow=True)

    # print the lines of output from the container as it runs
    for line in process:
        print(line.decode("utf-8").strip())


def find_frame_len(ch5_file: str):
    def find_time_lapse_len(name, obj):
        """
        Recursively search for a dataset named "time_lapse"
        within an HDF5 (or HDF5-like) file.

        Return the dataset object when found.
        """

        if isinstance(obj, h5py.Dataset):
            if "sample" in name and "time_lapse" in name:
                print("Found 'time_lapse' dataset at:", obj.name)
                # Return the dataset object
                return obj.size

        elif isinstance(obj, h5py.Group):
            # Traverse the group's children recursively
            for key, value in obj.items():
                # Recursively search within the group
                result = find_time_lapse_len(name, value)
                if result is not None:
                    # If "time_lapse" is found in a subgroup, return the result
                    return result

    # Open the HDF5 file in read-only mode
    with h5py.File(ch5_file, "r") as f:
        # Start the search from the root group
        return f.visititems(find_time_lapse_len)


def get_frame_tiff_from_idr_ch5(frame: str, local_frame_tif: str) -> str:
    """
    Gather IDR ch5 file and extract a frame as a TIFF, returning the local filepath
    and cleaning up the ch5 afterwards.

    Args:
        frame (str):
            The frame number to extract from the IDR ch5 file.
        local_frame_tif (str):
            The local filepath where the extracted TIFF will be saved.

    Returns:
        str:
            The local filepath of the extracted TIFF image.
    """

    print(
        "Working on",
        f"frame: {frame}",
        f"tiff: {local_frame_tif}",
    )

    # if we don't already have a file, create it
    if not pathlib.Path(
        (return_path := f"{image_download_dir}/{str(local_frame_tif)}")
    ).is_file():
        # extract a frame from the ch5 file using bfconvert through a docker container
        run_dockerfile_container(
            dockerfile="./5.data_packaging/Dockerfile.bfconvert",
            image_name="ome_bfconvert",
            volumes=[f"{os.getcwd()}/5.data_packaging/images/extracted_frame:/app"],
            command=(
                f"-timepoint {frame} {pathlib.Path(local_ch5_file).name} {str(local_frame_tif)}"
                " -overwrite"
            ),
        )

    return return_path


# modified from:
# https://github.com/WayScience/IDR_stream/blob/main/idrstream/preprocess.py#L194C1-L227C76
def get_ic_context_frames(target_frame: int, movie_len: int) -> List[int]:
    """
    Gather additional non-target frames for use with PyBasic IC.

    Note: frames are 0-indexed while movie length is not.
    """

    # "sandwich" the frames using one frame before and one frame after
    # the target frame provided from frame_num.
    if target_frame + 1 <= movie_len:
        return [target_frame - 1, target_frame, target_frame + 1]

    # else if we have the first frame, use two frames after
    elif target_frame == 0:
        return [target_frame, target_frame + 1, target_frame + 2]

    # otherwise we have the last frame, so use two frames prior
    else:
        return [target_frame - 2, target_frame - 1, target_frame]


# specify an image download dir and create it
image_download_dir = "./5.data_packaging/images/extracted_frame"
pathlib.Path(image_download_dir).mkdir(parents=True, exist_ok=True)

# specify an export dir and create it
export_dir = "./5.data_packaging/location_and_ch5_frame_image_data"
pathlib.Path(export_dir).mkdir(parents=True, exist_ok=True)

# get a table of image-relevant data
table = get_image_union_table()

# add additional frames for IC-based work which required multiple frames of context

# 0. group by movie file source
# 1. download movie
# 2. determine frame length
# 3. calculate additional non-target frames for IC
# 4. extract target and non-target frames for IC
# 5. read all frames as arrays for use within pybasic IC
# 6. run IC to gain IC image
# 7. read target frame and IC frame as blobs into file
# 8. read with tiffile, store in final table
# 9. remove movie file
# 10. remove raw images?

# iterate through location union data
for unique_file in pc.unique(table["IDR_FTP_ch5_location"]).to_pylist():

    # download the ch5 file
    local_ch5_file = retrieve_ftp_file(
        ftp_file=unique_file, download_dir=image_download_dir
    )

    # find the movie length
    movie_length = find_frame_len(ch5_file=local_ch5_file)

    # reference rows with the same ch5 file
    for batch in table.filter(
        pc.equal(table["IDR_FTP_ch5_location"], unique_file)
    ).to_batches(max_chunksize=1):

        # convert to a dictionary row
        # use a comprehension to access single values outside of a list
        row = batch.to_pydict()
        
        # reference a target frame as an integer
        target_frame = int(row["Frames"][0])

        # loop through frames to extract them
        frames_to_tiffs = {
            # for each frame, extract a tiff from the ch5
            frame: get_frame_tiff_from_idr_ch5(
                frame=frame,
                local_frame_tif=row["DNA_dotted_notation"][0].replace(
                    f"_{target_frame}.tif", f"_{frame}.tif"
                ),
            )
            # gather all frames based on a target frame
            for frame in get_ic_context_frames(
                target_frame=target_frame, movie_len=movie_length
            )
        }

        # create record batches from the frames_to_tiffs
        rows = [
            pa.RecordBatch.from_pydict(
                # retain data from original row if our frame matches the original
                row
                if row["Frames"][0] == str(frame_number)
                # otherwise, create new rows with relevant IC-focused frame data
                else {
                    key: (
                        [str(frame_number)]
                        if key == "Frames"
                        else (
                            [frame_tiff]
                            if key == "DNA_dotted_notation"
                            else ["IC_FRAME"] if key == "Frame_type" else val
                        )
                    )
                    for key, val in row.copy().items()
                }
            )
            for frame_number, frame_tiff in frames_to_tiffs.items()
        ]

        # write a table with the row baches
        parquet.write_table(
            # create a table from the row batches
            table=pa.Table.from_batches(rows),
            where=f"{export_dir}/",
        )

    # remove the ch5 file as we no longer need it
    # pathlib.Path(local_ch5_file).unlink()


# create a new table from awkward array to help join the multi-dim image data
"""table = ak.to_arrow_table(
    # join a pyarrow table as an awkward array with a new field for multi-dim tiff data
    ak.with_field(
        array=ak.from_arrow(array=table),
        what=[
            # read the tiff as a numpy array
            tifffile.imread(
                # gather tiff frame from ch5 for every row in location union data
                get_frame_tiff_from_idr_ch5(
                    frame=frame, ftp_file=ftp_file, local_frame_tif=local_frame_tif
                )
            )
            # iterate through location union data
            for (frame,), (ftp_file,), (local_frame_tif,) in table.select(
                ["Frames", "IDR_FTP_ch5_location", "DNA_dotted_notation"]
            ).to_batches(max_chunksize=1)
        ],
        # name the new field / column
        where="ch5_frame_tifffile_read_unaltered",
    )
)"""

# write the table to parquet file
"""parquet.write_table(
    table=table, where="5.data_packaging/location_and_ch5_frame_image_data.parquet"
)"""
