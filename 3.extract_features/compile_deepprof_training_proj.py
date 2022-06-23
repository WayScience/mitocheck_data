#!/usr/bin/env python
# coding: utf-8

# # DeepProfiler Project Compiler
# ### Compile a [DeepProfiler Project](https://cytomining.github.io/DeepProfiler-handbook/docs/2.%20Project%20structure.html) from training data
# 
# 
# #### Import libraries

# In[1]:


import pandas as pd
import pathlib

from PIL import Image
import shutil


# #### Define Functions for Compiling Project

# In[2]:


def get_gene(plate, well, annoations):
    target_gene = annoations[(annoations["Plate"]==plate) & (annoations["Well Number"]==str(int(well)))]["Original Gene Target"].item()
    if str(target_gene) == "nan":
        target_gene = "failed_QC"
    return target_gene

def compile_index_csv(preproc_training_path, annotations_path, save_path):
    """
    compile index.csv from training data used by DeepProfiler
    """
    index_csv_data = []
    annoations = pd.read_csv(annotations_path, compression='gzip', dtype=object)
    for plate_path in preproc_training_path.iterdir():
        for well_path in plate_path.iterdir():
            for frame_path in well_path.iterdir():
                for file_path in frame_path.iterdir():
                    index_csv_line = {
                        "Metadata_Plate": plate_path.name, 
                        "Metadata_Well": f"{well_path.name}_{frame_path.name}", 
                        "Metadata_Site": 1, 
                        "Plate_Map_Name": f"{plate_path.name}_{well_path.name}_{frame_path.name}",
                        "DNA": f"{plate_path.name}/{well_path.name}/{frame_path.name}/{file_path.name}",
                        "Gene": get_gene(plate_path.name, well_path.name, annoations),
                        "Gene_Replicate": 1
                        }
                    index_csv_data.append(index_csv_line)
    index_csv_data = pd.DataFrame(index_csv_data)
    save_path.parents[0].mkdir(parents=True, exist_ok=True)
    index_csv_data.to_csv(save_path, index=False)
    
def compile_training_locations(index_csv_path, segmentations_path, save_path):
    index_csv = pd.read_csv(index_csv_path)
    for index, row in index_csv.iterrows():
        plate = row["Metadata_Plate"]
        well_frame = row["Metadata_Well"]
        well = well_frame.split("_")[0]
        frame = well_frame.split("_")[1]
        site = row["Metadata_Site"]
        
        frame_segments_path = pathlib.Path(f"{segmentations_path}/{plate}/{well}/{frame}/{plate}_{well}_{frame}.tsv")
        try:
            frame_segments = pd.read_csv(frame_segments_path, delimiter="\t")
            frame_segments = frame_segments[['Location_Center_X', 'Location_Center_Y']]
            frame_segments = frame_segments.rename(columns={'Location_Center_X': 'Nuclei_Location_Center_X', 'Location_Center_Y': 'Nuclei_Location_Center_Y'})
            
            locations_save_path = pathlib.Path(f"{save_path}/{plate}/{well_frame}-{site}-Nuclei.csv")
            locations_save_path.parents[0].mkdir(parents=True, exist_ok=True)
            frame_segments.to_csv(locations_save_path, index=False)
        except FileNotFoundError:
            print(f"No tsv for {frame_segments_path}")


# #### Compile index.csv file

# In[3]:


preproc_training_path = pathlib.Path("../1.preprocess_data/labeled_frames_preprocessed/")
annoations_path = pathlib.Path("idr0013-screenA-annotation.csv.gz")
save_path = pathlib.Path("inputs/metadata/index.csv")
compile_index_csv(preproc_training_path, annoations_path, save_path)
print("Done compiling index.csv!")


# #### Copy images to DeepProfiler Project

# In[4]:


preproc_training_path = pathlib.Path("../1.preprocess_data/labeled_frames_preprocessed/")
deepprof_images_path = pathlib.Path("inputs/images/")
shutil.copytree(preproc_training_path, deepprof_images_path)
print("Done copying images!")


# #### Compile Training Locations Data

# In[5]:


index_csv_path = pathlib.Path("inputs/metadata/index.csv")
segmentations_path = pathlib.Path("../2.segment_nuclei/segmented/")
save_path = pathlib.Path("inputs/locations/")
compile_training_locations(index_csv_path, segmentations_path, save_path)
print("Done compiling locations!")

