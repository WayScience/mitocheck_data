"""
Python module for gathering images from Image Data Resource (IDR).
"""

import os
import pathlib
import warnings
from ftplib import FTP
from typing import List

import docker
import duckdb
import h5py
import numpy as np
import pyarrow as pa
import pyarrow.compute as pc
import pybasic
import skimage
from constants import (
    DOCKER_PLATFORM,
    FTP_IDR_MITOCHECK_CH5_DIR,
    FTP_IDR_URL,
    FTP_IDR_USER,
)
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

    # if we don't already have the file, download it
    if not pathlib.Path(download_filepath).is_file():
        try:
            # Connect to the FTP server
            with FTP(ftp_url) as ftp:
                # Log in to the FTP server
                ftp.login(user=ftp_user, passwd=ftp_pass)

                # Open a local file for writing in binary mode
                with open(download_filepath, "wb") as local_file:
                    # Download the file from the FTP server
                    ftp.retrbinary(f"RETR {ftp_file}", local_file.write)

        except Exception as e:
            print("An error occurred:", e)

    # return the download filepath
    return download_filepath


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
                'TARGET_FRAME' as Frame_type,
                ''::BLOB as Frame_tiff
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
    """
    Find the length of the 'time_lapse' dataset within an HDF5 file.

    This function recursively searches for a dataset named 'time_lapse' within
    the provided HDF5 (or HDF5-like) file. Once found, it returns the size of
    the dataset, which represents the number of frames.

    Args:
        ch5_file (str): The path to the HDF5 file to be searched.

    Returns:
        int: The length of the 'time_lapse' dataset (number of frames).

    Example:
        >>> find_frame_len('example.h5')
        100

    Note:
        This function returns None if the 'time_lapse' dataset is not found
        within the HDF5 file.
    """

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


def get_frame_tiff_from_idr_ch5(
    frame: str, local_ch5_file: str, local_frame_tif: str
) -> str:
    """
    Gather IDR ch5 file and extract a frame as a TIFF, returning the local filepath
    and cleaning up the ch5 afterwards.

    Args:
        frame (str):
            The frame number to extract from the IDR ch5 file.
        local_ch5_file (str):
            The local filepath where the ch5 file may be referenced.
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
    if not pathlib.Path(local_frame_tif).is_file():
        # extract a frame from the ch5 file using bfconvert through a docker container
        run_dockerfile_container(
            dockerfile="./5.data_packaging/Dockerfile.bfconvert",
            image_name="ome_bfconvert",
            volumes=[f"{os.getcwd()}:/app"],
            command=(
                f"-timepoint {frame} {local_ch5_file} {str(local_frame_tif)}"
                " -overwrite"
            ),
        )

    return local_frame_tif


# modified from:
# https://github.com/WayScience/IDR_stream/blob/main/idrstream/preprocess.py#L194C1-L227C76
def get_ic_context_frames(target_frame: int, movie_len: int) -> List[int]:
    """
    Gather additional non-target frames for use with PyBasic IC.

    This function returns a list of three frames: one frame before the target frame,
    the target frame itself, and one frame after the target frame. The frames are
    0-indexed, while the movie length is not. If the target frame is the first frame
    (0), it returns the target frame and the next two frames. If the target frame is
    the last frame, it returns the target frame and the two preceding frames.

    Args:
        target_frame (int):
            The index of the target frame (0-indexed).
        movie_len (int):
            The length of the movie (1-indexed).

    Returns:
        List[int]:
            A list of three frame indices for context.

    Example:
        >>> get_ic_context_frames(2, 5)
        [1, 2, 3]

        >>> get_ic_context_frames(0, 5)
        [0, 1, 2]

        >>> get_ic_context_frames(4, 5)
        [2, 3, 4]
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


# referenced with modifications
# from: https://github.com/WayScience/IDR_stream/blob/main/idrstream/preprocess.py#L114
def pybasic_IC_target_frame_to_tiff(
    frames_as_arrays: List[np.ndarray], target_frame: int, destination_filename: str
):
    """
    PyBaSiC Illumination correction as described in http://www.nature.com/articles/ncomms14836

    Parameters
    ----------
    frames_as_arrays : List[np.ndarray]
        array of frames to perform illumination correction on
    target_frame : int
        target frame within the context of the frames_as_arrays
        to return.
    destination_filename : str
        export the target_frame to a destination filepath specified
        through this parameter.

    Returns
    -------
    str
        filepath with the IC image as tiff
    """
    # capture pybasic warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        flatfield, darkfield = pybasic.basic(
            frames_as_arrays, darkfield=True, verbosity=False
        )
        baseflour = pybasic.background_timelapse(
            images_list=frames_as_arrays,
            flatfield=flatfield,
            darkfield=darkfield,
            verbosity=False,
        )
        brightfield_images_corrected_original = pybasic.correct_illumination(
            images_list=frames_as_arrays,
            flatfield=flatfield,
            darkfield=darkfield,
            background_timelapse=baseflour,
        )

        # convert corrected images to numpy array, normalize, and convert to uint8
        brightfield_images_corrected = np.array(brightfield_images_corrected_original)
        brightfield_images_corrected[brightfield_images_corrected < 0] = (
            0  # make negatives 0
        )
        brightfield_images_corrected = brightfield_images_corrected / np.max(
            brightfield_images_corrected
        )  # normalize the data to 0 - 1
        brightfield_images_corrected = (
            255 * brightfield_images_corrected
        )  # Now scale by 255
        corrected_movie = brightfield_images_corrected.astype(np.uint8)

        # export the target frame to file
        skimage.io.imsave(fname=destination_filename, arr=corrected_movie[target_frame])

        # return the filepath
        return destination_filename


def read_image_as_binary(image_path: str) -> bytes:
    """
    Reads an image file and returns its content as binary data.

    Args:
        image_path (str): The path to the image file to be read.

    Returns:
        bytes: The binary content of the image file.

    Example:
        binary_data = read_image_as_binary("path/to/image.jpg")
        print(binary_data)
    """
    with open(image_path, "rb") as f:
        return f.read()


# specify an image download dir and create it
image_download_dir = "./5.data_packaging/images/extracted_frame"
pathlib.Path(image_download_dir).mkdir(parents=True, exist_ok=True)

# specify an export dir and create it
export_dir = "./5.data_packaging/location_and_ch5_frame_image_data"
pathlib.Path(export_dir).mkdir(parents=True, exist_ok=True)

# get a table of image-relevant data
table = get_image_union_table()

# add additional frames for IC-based work which required multiple frames of context
#
# Steps are roughly:
#
# 0. group by movie file source
# 1. download movie
# 2. determine frame length
# 3. calculate additional non-target frames for IC
# 4. extract target and non-target frames for IC
# 5. read all frames as arrays for use within pybasic IC
# 6. run IC to gain IC image
# 8. store the data within a table including blobs for target and IC images
# 9. remove frame images
# 10. remove ch5 file

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
            str(frame): get_frame_tiff_from_idr_ch5(
                frame=frame,
                local_ch5_file=local_ch5_file,
                local_frame_tif=(
                    f"{image_download_dir}/"
                    + row["DNA_dotted_notation"][0].replace(
                        f"_{target_frame}.tif", f"_{frame}.tif"
                    )
                ),
            )
            # gather all frames based on a target frame
            for frame in get_ic_context_frames(
                target_frame=target_frame, movie_len=movie_length
            )
        }

        # read the tiffs as arrays for use with pybasic
        # and then add the IC image filepath as a new
        # element along with the others
        frames_to_tiffs[f"{target_frame}_IC"] = pybasic_IC_target_frame_to_tiff(
            frames_as_arrays=[
                skimage.io.imread(fname=tiff_file)
                for tiff_file in frames_to_tiffs.values()
            ],
            target_frame=list(
                idx
                for idx, frame in enumerate(frames_to_tiffs.keys())
                if frame == str(target_frame)
            )[0],
            destination_filename=(
                f"{image_download_dir}/"
                + row["DNA_dotted_notation"][0].replace(
                    f"_{target_frame}.tif", f"_{target_frame}_IC.tif"
                )
            ),
        )

        # create record batches from the frames_to_tiffs
        rows = [
            pa.RecordBatch.from_pydict(
                # retain data from original row if our frame matches the original
                {
                    **row,
                    "Frame_tiff": [read_image_as_binary(image_path=frame_tiff)],
                }
                if row["Frames"][0] == str(frame_number)
                # otherwise, create new rows with relevant IC-focused frame data
                else {
                    **row,
                    "Frames": [str(frame_number)],
                    "DNA_dotted_notation": [frame_tiff],
                    "Frame_type": (
                        ["IC_FRAME"]
                        if "_IC" not in frame_number
                        else ["IC_TARGET_FRAME"]
                    ),
                    "Frame_tiff": [read_image_as_binary(image_path=frame_tiff)],
                }
            )
            for frame_number, frame_tiff in frames_to_tiffs.items()
        ]

        # write a table with the row baches
        parquet.write_table(
            # create a table from the row batches
            table=pa.Table.from_batches(rows),
            where=f"{export_dir}/{pathlib.Path(local_ch5_file).stem}.frame_{row['Frames'][0]}.parquet",
        )

        # remove the tiff files as we no longer need them
        """for tiff in frames_to_tiffs.values():
            pathlib.Path(tiff).unlink()"""

    # remove the ch5 file as we no longer need it
    # pathlib.Path(local_ch5_file).unlink()
