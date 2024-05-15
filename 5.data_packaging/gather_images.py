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

    try:
        # Connect to the FTP server
        with FTP(ftp_url) as ftp:
            # Log in to the FTP server
            ftp.login(user=ftp_user, passwd=ftp_pass)

            # Specify the file to download
            download_filepath = f"{download_dir}/{pathlib.Path(ftp_file).name}"

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
                ) AS IDR_FTP_ch5_location
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


def get_frame_tiff_from_idr_ch5(frame: str, ftp_file: str, local_frame_tif: str) -> str:
    """
    Gather IDR ch5 file and extract a frame as a TIFF, returning the local filepath
    and cleaning up the ch5 afterwards.

    Args:
        frame (str):
            The frame number to extract from the IDR ch5 file.
        ftp_file (str):
            The name of the IDR ch5 file to retrieve.
        local_frame_tif (str):
            The local filepath where the extracted TIFF will be saved.

    Returns:
        str:
            The local filepath of the extracted TIFF image.
    """

    print(
        "Working on ",
        f"frame: {frame}",
        f"ftp file: {ftp_file}",
        f"tiff: {local_frame_tif}",
    )
    # download the ch5 file
    local_ch5_file = retrieve_ftp_file(
        ftp_file=str(ftp_file), download_dir=image_download_dir
    )

    # extract a frame from the ch5 file using bfconvert through a docker container
    run_dockerfile_container(
        dockerfile="./5.data_packaging/Dockerfile.bfconvert",
        image_name="ome_bfconvert",
        volumes=[f"{os.getcwd()}/5.data_packaging/images/extracted_frame:/app"],
        command=f"-timepoint {frame} {pathlib.Path(local_ch5_file).name} {str(local_frame_tif)}",
    )

    # remove the ch5 file as we no longer need it
    pathlib.Path(local_ch5_file).unlink()

    return f"{image_download_dir}/{str(local_frame_tif)}"


# specify an image download dir and create it
image_download_dir = "./5.data_packaging/images/extracted_frame"
pathlib.Path(image_download_dir).mkdir(parents=True, exist_ok=True)

# get a table of image-relevant data
table = get_image_union_table()

# create a new table from awkward array to help join the multi-dim image data
table = ak.to_arrow_table(
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
        where="ch5_frame_tiff_unaltered",
    )
)

# write the table to parquet file
parquet.write_table(
    table=table, where="5.data_packaging/location_and_ch5_frame_image_data.parquet"
)
