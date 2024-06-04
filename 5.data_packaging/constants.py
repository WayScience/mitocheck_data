"""
Create various constants for use during data packaging.
"""

# list of files to be processed
DATA_FILES = [
    "mitocheck_metadata/features.samples.txt",
    "mitocheck_metadata/features.samples-w-colnames.txt",
    "mitocheck_metadata/idr0013-screenA-annotation.csv.gz",
    "0.locate_data/locations/negative_control_locations.tsv",
    "0.locate_data/locations/positive_control_locations.tsv",
    "0.locate_data/locations/training_locations.tsv",
    "1.idr_streams/stream_files/idr0013-screenA-plates.tsv",
    "1.idr_streams/stream_files/idr0013-screenA-plates-w-colnames.tsv",
    "2.format_training_data/results/training_data__ic.csv.gz",
    "2.format_training_data/results/training_data__no_ic.csv.gz",
    "3.normalize_data/normalized_data/training_data__ic.csv.gz",
    "3.normalize_data/normalized_data/training_data__no_ic.csv.gz",
    "4.analyze_data/results/compiled_2D_umap_embeddings.csv",
    "4.analyze_data/results/single_cell_class_counts.csv",
]

# create a copy of the data files, removing any which don't include column names
DATA_FILES_W_COLNAMES = [
    file
    for file in DATA_FILES
    if file
    not in [
        "mitocheck_metadata/features.samples.txt",
        "1.idr_streams/stream_files/idr0013-screenA-plates.tsv",
    ]
]

PACKAGING_DATASETS = ["5.data_packaging/location_and_ch5_frame_image_data"]

# FTP resources for accessing IDR
# See here for more:
# https://idr.openmicroscopy.org/about/download.html
FTP_IDR_URL = "ftp.ebi.ac.uk"
FTP_IDR_USER = "anonymous"
FTP_IDR_MITOCHECK_CH5_DIR = (
    "/pub/databases/IDR/idr0013-neumann-mitocheck/20150916-mitocheck-analysis/mitocheck"
)

DOCKER_PLATFORM = "linux/amd64"
