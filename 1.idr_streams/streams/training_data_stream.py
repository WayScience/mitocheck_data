# import libraries
import pathlib
import pandas as pd
import shutil
import logging

import sys
sys.path.append("../IDR_stream/")
from idrstream.idr_stream import IdrStream

# set up idr stream
idr_id = "idr0013"
tmp_dir = pathlib.Path("../tmp/")
try:
    shutil.rmtree(tmp_dir)
except:
    pass

final_data_dir = pathlib.Path("../extracted_features/")
training_data_final_dir = pathlib.Path(
    f"{final_data_dir}/training_data/"
)

stream = IdrStream(
    idr_id,
    tmp_dir,
    training_data_final_dir,
    log="logs/training_idr_stream.log",
)

stream_files_dir = pathlib.Path("../stream_files/")

aspera_path = pathlib.Path("/home/roshankern/.aspera/ascli/sdk/ascp")
aspera_key_path = pathlib.Path(f"{stream_files_dir}/asperaweb_id_dsa.openssh")
screens_path = pathlib.Path(f"{stream_files_dir}/idr0013-screenA-plates.tsv")

stream.init_downloader(aspera_path, aspera_key_path, screens_path)

fiji_path = pathlib.Path("/home/roshankern/Desktop/Fiji.app")
stream.init_preprocessor(fiji_path)

nuclei_model_specs = {
    "model_type": "cyto",
    "channels": [0, 0],
    "diameter": 0,
    "flow_threshold": 0.8,
    "cellprob_threshold": 0,
    "remove_edge_masks": True,
}
stream.init_segmentor(nuclei_model_specs)

config_path = pathlib.Path(
    f"{stream_files_dir}/DP_files/mitocheck_profiling_config.json"
)
checkpoint_path = pathlib.Path(
    f"{stream_files_dir}/DP_files/efficientnet-b0_weights_tf_dim_ordering_tf_kernels_autoaugment.h5"
)
stream.copy_DP_files(config_path, checkpoint_path)

locations_dir = pathlib.Path("../../0.locate_data/locations/")
training_locations_path = pathlib.Path(
    f"{locations_dir}/training_locations.tsv"
)
training_data = pd.read_csv(
    training_locations_path, sep="\t", index_col=0
)

# run idr stream
stream.run_stream(training_data, batch_size=5, start_batch=0)
