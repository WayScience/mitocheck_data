# 5. Data Packaging

In this module, we collect and package data created by this project.
Packaging involves the process of making the data easier to both store and use by others.
This portion of the project strives to be additive-only, attempting "First do no harm." through "yes and" focus.

A story to help describe goals:

_"As a research data participant I need a way to analyze (understand, contextualize, and explore) and implement (engineer solutions which efficiently scale for time and computing resources) the data found here in order to effectively reproduce findings, make new discoveries, and avoid challenging (or perhaps incorrect) translations individually."_

We tried to think about the "research data participant" here with empathy; we can reduce barriers for other people by readying the data for use outside of this project.
If the barriers are high, a person may use the data incorrectly or opt to not use it at all.
We can't know all the reasons why or how someone might use the findings here but we can empathize for them through how much time cost they may face to use it.
A side-effect of thinking this way is that we also can benefit one another (we all face similar challenges).

Proposed solutions:

- Use named column data tables at a bare minimum to increase data understandability by the audience.
- Use data-typed in-memory and file-based formats to ensure consistent handling of data once read from (potentially  un-typed) data sources.
- Store data in high-performance file-formats for distribution and scalable implementation by other people.
- Share data schema upfront to indicate data translation outside of in-process observation.
- Containerize OS-level dependencies to ensure reproducibility.
- Rewrite IDR data extraction to use FTP as a simple and currently documented procedure.
- Create avenues for reuse where possible to help increase the chances of multiplied benefit beyond just this PR.

## Development

This module leverages system-available Python, [Poetry](https://github.com/python-poetry/poetry), and [Poe the Poet](https://poethepoet.natn.io/index.html) (among other dependencies found in the `pyproject.toml` file) to complete tasks.
This module also leverages Docker to reproducibly leverage additional tooling outside of Python dependencies.
We recommend installing Docker (suggested through [Docker Desktop](https://www.docker.com/products/docker-desktop/)), Python (suggested through [pyenv](https://github.com/pyenv/pyenv)) and Poetry (suggested through `pip install poetry`), then using the following to run the processes related to this step.

```sh
# note: run these from the project root (one directory up).
# after installing poetry, create the environment
poetry install

# run the poe the poet task related to this step
# (triggers multiple Python modules)
poetry run poe package_data
```

## Data Assets

The following data assets are included as part of the data package.

- mitocheck_metadata/features.samples-w-colnames.txt
- mitocheck_metadata/idr0013-screenA-annotation.csv.gz
- 0.locate_data/locations/negative_control_locations.tsv
- 0.locate_data/locations/positive_control_locations.tsv
- 0.locate_data/locations/training_locations.tsv
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

## Data Asset Column Labeling

Some data assets are duplicated to help label their columns where the originals may not include them.
These column names help provide context on what the row values contain and make working with the data more observable within Arrow, Lance, and other technologies used here.
These are presented below as pairs (with the `-w-colnames` indicating data which uses updated labeling for column names).

- mitocheck_metadata/features.samples.txt
- mitocheck_metadata/features.samples-w-colnames.txt
- 1.idr_streams/stream_files/idr0013-screenA-plates.tsv
- 1.idr_streams/stream_files/idr0013-screenA-plates-w-colnames.tsv
