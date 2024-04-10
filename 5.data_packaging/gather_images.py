"""
Python module for gathering images from Image Data Resource (IDR).
"""

import os
import pathlib
from ftplib import FTP
from typing import List

import docker
import duckdb
import pyarrow as pa
from constants import (
    DOCKER_PLATFORM,
    FTP_IDR_MITOCHECK_CH5_DIR,
    FTP_IDR_URL,
    FTP_IDR_USER,
)


def retrieve_ftp_file(
    ftp_file: str,
    download_dir: str,
    ftp_url: str = FTP_IDR_URL,
    ftp_user: str = FTP_IDR_USER,
    ftp_pass: str = "",
) -> str:
    """
    Retrieve a file using FTP
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
    # build a table with relevant information to extract images
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
    Build, run, and stream logs from a Dockerfile-based container
    """

    print(
        f"Running Docker container {image_name} based on {dockerfile} with command {command}."
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


# specify an image download dir and create it
image_download_dir = "./5.data_packaging/images/extracted_frame"
pathlib.Path(image_download_dir).mkdir(parents=True, exist_ok=True)

# get a table of image-relevant data
table = get_image_union_table()

# unpack tuples in batches of 1 for row-wise operations from the table
for (frame,), (ftp_file,), (local_frame_tif,) in table.select(
    ["Frames", "IDR_FTP_ch5_location", "DNA_dotted_notation"]
).to_batches(max_chunksize=1):
    print("Working on: ", frame, ftp_file, local_frame_tif)
    # download the ch5 file
    local_file = retrieve_ftp_file(
        ftp_file=str(ftp_file), download_dir=image_download_dir
    )

    run_dockerfile_container(
        dockerfile="./5.data_packaging/Dockerfile.bfconvert",
        image_name="ome_bfconvert",
        volumes=[f"{os.getcwd()}/5.data_packaging/images/extracted_frame:/app"],
        command=f"-timepoint {frame} {pathlib.Path(local_file).name} {local_frame_tif}",
    )
