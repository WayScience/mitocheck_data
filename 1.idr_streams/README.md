# 1. IDR Streams

In this module, we use [idrstream](https://github.com/WayScience/IDR_stream) to extract features from the training and control mitocheck data.\

`idrstream` uses various tools to download, preprocess, segment, and extract features from the frames, wells, plates (metadata) curated in [0.locate_data](../0.locate_data).
The tool used to extract features, [DeepProfiler](https://github.com/cytomining/DeepProfiler), requires the desired frame along with intermediate files to understand where cells are located and how to extract features.
These files can reach TB of size for feature extraction on larger datasets.
`idrstream` processes IDR data in batches to avoid the need for storing many intermediate files at once.
However, the intermediate files for each batch still need to be stored locally.
The intermediate files for the training and control datasets will be stored in `tmp/`.

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

# Use specific version of idrstream
git clone https://github.com/WayScience/IDR_stream.git
cd IDR_stream
git checkout d5b049b308a468f6a80f7657c4cb625770130129
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
bash idr_streams.sh
```

### IDR Stream Notes

Logs from each `idrstream` run will be saved to [logs/](streams/logs/).
These logs inlcude info about each `idrstream` run, including any errors that might have occured while profiling a batch.
The example logs located in [logs/](streams/logs/) only include information from batch 0 of each `idrstream` because these IDR streams were originally run as a prototype and thus had no log file.

IDR stream run times:
- training data: 64 min
- negative controls: 900 min
- negative controls: 515 min

These IDR streams were run with the following specs:

- 24 CPUs
- 64 GB RAM
- ~ 650 MB/s download speed (as measured by [speedtest.net](https://www.speedtest.net/)).
- GeForce RTX 3090 sm_86 with following output from nvidia-smi:
```
+-----------------------------------------------------------------------------+
| NVIDIA-SMI 470.129.06   Driver Version: 470.129.06   CUDA Version: 11.4     |
|-------------------------------+----------------------+----------------------+
| GPU  Name        Persistence-M| Bus-Id        Disp.A | Volatile Uncorr. ECC |
| Fan  Temp  Perf  Pwr:Usage/Cap|         Memory-Usage | GPU-Util  Compute M. |
|                               |                      |               MIG M. |
|===============================+======================+======================|
|   0  NVIDIA GeForce ...  Off  | 00000000:2D:00.0  On |                  N/A |
|  0%   49C    P8    44W / 420W |    590MiB / 24259MiB |     10%      Default |
|                               |                      |                  N/A |
+-------------------------------+----------------------+----------------------+
```