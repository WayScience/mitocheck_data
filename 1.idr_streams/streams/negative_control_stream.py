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
# tmp dir contains intermediate files (desired frame, nuclei locations, DeepProfiler files)
tmp_dir = pathlib.Path("../tmp/")
try:
    shutil.rmtree(tmp_dir)
except:
    pass

final_data_dir = pathlib.Path("../extracted_features/")
negative_control_data_final_dir = pathlib.Path(
    f"{final_data_dir}/negative_control_data/"
)

stream = IdrStream(
    idr_id,
    tmp_dir,
    negative_control_data_final_dir,
    log="logs/negative_control_idr_stream.log",
)

stream_files_dir = pathlib.Path("../stream_files/")
# path to /home/user
home_dir = pathlib.Path.home()

aspera_path = pathlib.Path(f"{home_dir}/.aspera/ascli/sdk/ascp")
aspera_key_path = pathlib.Path(f"{stream_files_dir}/asperaweb_id_dsa.openssh")
screens_path = pathlib.Path(f"{stream_files_dir}/idr0013-screenA-plates.tsv")

stream.init_downloader(aspera_path, aspera_key_path, screens_path)

fiji_path = pathlib.Path(f"{home_dir}/Desktop/Fiji.app")
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
negative_control_locations_path = pathlib.Path(
    f"{locations_dir}/negative_control_locations.tsv"
)
negative_control_data = pd.read_csv(
    negative_control_locations_path, sep="\t", index_col=0
)

# run idr stream
stream.run_stream(negative_control_data, batch_size=10, start_batch=0)
# clear tmp dir
shutil.rmtree(tmp_dir)