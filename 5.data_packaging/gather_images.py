"""
Python module for gathering images from Image Data Resource (IDR).
"""

from ftplib import FTP
import pathlib
import pyarrow as pa

import duckdb
from constants import FTP_IDR_URL, FTP_IDR_USER, FTP_IDR_MITOCHECK_CH5_DIR


import shutil
import sys
from typing import List

import anyio
import dagger


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


# referenced with modifications from:
# https://docs.dagger.io/sdk/python/628797/get-started
async def run_bfconvert(
    bfconvert_opts: List[str],
    source_convert_filepath: str,
    dest_convert_filepath: str,
    source_volume_mount_dir: str,
    debug: bool,
) -> None:
    """
    Dagger pipeline for running containerized work
    """

    # create dagger conf based on debug arg
    dagger_conf = dagger.Config(log_output=sys.stderr) if debug else dagger.Config()

    async with dagger.Connection(dagger_conf) as client:
        # get reference to the local project
        dockerfile_dir = client.host().directory(".")

        # build a python container based on Dockerfile and run test
        container = (
            client.container(
                # explicitly set the container to be a certain platform type
                platform=dagger.Platform("linux/amd64")
            )
            .build(
                context=dockerfile_dir,
                # uses a dockerfile to create the container
                dockerfile="./5.data_packaging/Dockerfile.bfconvert",
            )
            .with_mounted_directory(
                path="/app", source=client.host().directory(source_volume_mount_dir)
            )
            # run the python test through a poetry environment
            .with_exec(
                bfconvert_opts + [source_convert_filepath, dest_convert_filepath]
            )
        )

        # execute and show the results of the last executed command
        result = await container.stdout()
        await container.sync()

    print(result)


if __name__ == "__main__":

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
        """local_file = retrieve_ftp_file(
            ftp_file=str(ftp_file), download_dir=image_download_dir
        )"""

        local_file = "./5.data_packaging/images/extracted_frame/00015_01.ch5"

        anyio.run(
            run_bfconvert,
            # options for bfconvert
            # see here for more:
            # https://bio-formats.readthedocs.io/en/stable/users/comlinetools/conversion.html
            ["-timepoint", str(frame)],
            # source file to use with bfconvert
            pathlib.Path(local_file).name,
            # destination file to use with bfconvert
            str(local_frame_tif),
            # local source volume dir for use with bfconvert container
            image_download_dir,
            # debug mode
            True,
        )
