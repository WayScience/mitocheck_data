# 5. Data Packaging

In this module, we collect and package data created by this project.
Packaging involves the process of making the data easier to both store and use by others.

## Data Assets

The following data assets are included as part of the data package.

- 0.locate_data/locations/negative_control_locations.tsv
- 0.locate_data/locations/positive_control_locations.tsv
- 0.locate_data/locations/training_locations.tsv
- 1.idr_streams/stream_files/idr0013-screenA-plates.tsv
- 1.idr_streams/stream_files/idr0013-screenA-plates-w-colnames.tsv
- 2.format_training_data/results/training_data__ic.csv.gz
- 2.format_training_data/results/training_data__no_ic.csv.gz
- 3.normalize_data/normalized_data/training_data__ic.csv.gz
- 3.normalize_data/normalized_data/training_data__no_ic.csv.gz
- 4.analyze_data/results/compiled_2D_umap_embeddings.csv
- 4.analyze_data/results/single_cell_class_counts.csv

## Schema

The schema for the data assets mentioned above are stored as references to help understand how the data will translate into various databases or collections of data.
This information may be found within the `5.data_packaging/schema` directory as text versions of PyArrow Table schemas.
