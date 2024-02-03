# 1. IDR Streams

In this module, we use [idrstream](https://github.com/WayScience/IDR_stream) to extract features from the training and control mitocheck data.\

`idrstream` uses various tools to download, preprocess, segment, and extract features from the frames, wells, plates (metadata) curated in [0.locate_data](../0.locate_data).
The tool used to extract features, [DeepProfiler](https://github.com/cytomining/DeepProfiler), requires the desired frame along with intermediate files to understand where cells are located and how to extract features.
These files can reach TB of size for feature extraction on larger datasets.
`idrstream` processes IDR data in batches to avoid the need for storing many intermediate files at once.
However, the intermediate files for each batch still need to be stored locally.
The intermediate files for the training and control datasets will be stored in `tmp/`.

In [streams/](streams/) we initialize and run `idrstream` for the training, negative control, and positive control data.
The `batch_size` parameter tells `idrstream` how many frames to process in one batch.
We set this to `10` for MitoCheck data, meaning that the features for cells in 10 images (unique plate/well/frame combination) are extracted in each batch.

We set `perform_illumination_correction` equal to `True` or `False` depending on the datset type we are extracting (`ic` or `no_ic`).
Because the impact of irregular illumination and PyBasic illumination correction are unclear, we compare the performance of models trained on `ic` and `no_ic` datasets in [phenotypic_profiling_model](https://github.com/WayScience/phenotypic_profiling_model).

## Step 1: Set up `idrstream`

`idrstream` is currently in development and needs to be installed via github.
Clone `idrstream` with the following commands:

```sh
# Make sure you are located in 1.idr_streams
cd 1.idr_streams

# Activate mitocheck_data conda environment
conda activate mitocheck_data

# clone IDR_stream
git clone https://github.com/WayScience/IDR_stream.git
# Use specific version of IDR_stream
cd IDR_stream
git checkout b10a7a8bf75ca2375dcf629a0c26d268fa3273d1
```

Follow the instructions at [idrstream setup](https://github.com/WayScience/IDR_stream#setup) to complete the idrstream setup.

## Step 2: Run IDR streams

Use the commands below to use `idrstream` to extract features from training and control frames:

```sh
# Make sure you are located in 1.idr_streams
cd 1.idr_streams

# Run IDR streams
bash idr_streams.sh
```

### IDR Stream Notes

Logs from each `idrstream` run will be saved to [logs/](streams/logs/).
These logs inlcude info about each `idrstream` run, including any errors that might have occured while profiling a batch.

Approximate IDR stream DP run times (CP and DP streams have nearly equivalent runtimes):
- training data: 65 min
- negative controls: 900 min
- positive controls: 650 min

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