# 1. IDR Streams

In this module, we use [idrstream](https://github.com/WayScience/IDR_stream) to extract features from the training and control mitocheck data.
`idrstream` uses various tools to download, preprocess, segment, and extract features from the frames, wells, plates (metadata) curated in [0.locate_data](../0.locate_data).

In [streams/](streams/) we initialize and run `idrstream` for the training, negative control, and positive control data.
The `batch_size` parameter tells `idrstream` how many wells to process in one batch.
We set this parameter to `5` for training data and `10` for control data because training data tends to have multiple frames to process per well whereas control data only has 1 frame to process per well.

## Step 1: Set up `idrstream`

`idrstream` is currently in development and needs to be installed via github.
Clone `idrstream` with the following commands:

```sh
# Make sure you are located in 1.idr_streams
cd 1.idr_streams

# Activate mitocheck_data conda environment
conda activate mitocheck_data

# Clone idrstream
git clone https://github.com/WayScience/IDR_stream.git
```

Follow the instructions at [idrstream setup](https://github.com/WayScience/IDR_stream#setup) to complete the `idrstream` setup.
The first step (necessary packages) does not need to be completed as the `mitocheck_data` environment includes all of these packages.

## Step 2: Run IDR streams

Use the commands below to locate training and control movies:

```sh
# Make sure you are located in 1.idr_streams
cd 1.idr_streams

# Activate mitocheck_data conda environment
conda activate mitocheck_data

# Run IDR streams
```


IDR stream runs:

training data: 64 min, no errors
negative controls: 900 min, 16 batches cancelled with errors
negative controls: 515 min, 14 batches cancelled with errors