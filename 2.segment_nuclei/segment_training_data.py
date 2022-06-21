#!/usr/bin/env python
# coding: utf-8

# ### Import Libraries

# In[33]:


#from cellpose.io import logger_setup
from cellpose import models, core, io, utils

import pathlib
import pandas as pd


# ### Define Segmentation Functions

# In[34]:


def get_frame_features_file(features_path, plate, well, frame):
    movie_path = pathlib.Path(f"{features_path}/{plate}/features/{well}/")
    frame_time = (int(frame)-1)*30
    frame_time_string = f"T{str(frame_time).zfill(5)}"
    
    for frame_file in movie_path.iterdir():
        if(frame_time_string in frame_file.name):
            return frame_file

def get_frame_labels(training_set_dat_path, plate, well, frame):
    well_string = f"W{str(well).zfill(5)}"
    frame_time = (int(frame)-1)*30
    frame_time_string = f"T{str(frame_time).zfill(5)}"
    frame_file_details = [plate, well_string, frame_time_string]
    
    frame_objects = []
    with open(training_set_dat_path) as trainingset_file:
        append = False
        for line in trainingset_file:
            if append and ".tif" in line:
                append = False
            if append:
                object_details = line.strip().split(": ")
                frame_objects.append(object_details)
            #match plate, well, frame to file name
            if all(detail in line for detail in frame_file_details):
                print(line.strip()) #starting line for movie labels
                append = True
    return frame_objects

def is_labeled(centroid, frame_features, frame_labels):
    """
    returns true if nucleus is included in labeled training data, false if not
    """
    objID = -1
    labeled = False
        
    #determine if centroid is inside any of labeled bounding boxes
    x = centroid[0]
    y = centroid[1]
    for labels in frame_labels:
        labeled_feature = frame_features[frame_features[0] == int(labels[0])]
        upperLeft_x = labeled_feature.iloc[0][1]
        upperLeft_y = labeled_feature.iloc[0][2]
        width = labeled_feature.iloc[0][3]
        height = labeled_feature.iloc[0][4]
        bottomRight_x = upperLeft_x + width
        bottomRight_y = upperLeft_y + height
        if upperLeft_x <= x and x <= bottomRight_x:
            if y >= upperLeft_y and y <= bottomRight_y:
                objID = labeled_feature.iloc[0][0]
                labeled = True
        
    return objID, labeled

def get_nuclei_locations(load_path, features_path, training_set_dat_path, cellpose_model, plate, well, frame):
    """
    returns nuclei location data in CellProfiler IdentifyPrimaryObjects format as pandas dataframe
    ie: ImageNumber, ObjectNumber, Location_Center_X, Location_Center_Y, Location_Center_Z
    """
    nuclei_data = []
    
    #use cellpose to get nuclei outlines
    channels = [0,0]
    frame_image = io.imread(load_path)
    masks, flows, styles, diams = cellpose_model.eval(frame_image, diameter=0, channels=channels, flow_threshold=0.8)
    outlines = utils.outlines_list(masks)
    
    frame_features_path = get_frame_features_file(features_path, plate, well, frame)
    print(frame_features_path)
    frame_features = pd.read_csv(frame_features_path, compression='gzip', header=None)
    frame_labels = get_frame_labels(training_set_dat_path, plate, well, frame)
    for outline in outlines:
        centroid = outline.mean(axis=0)
        objId, cell_is_labeled = is_labeled(centroid, frame_features, frame_labels)
        
        if cell_is_labeled:
            nucleus_data = {
                        "ImageNumber": 1, 
                        "ObjectNumber": len(nuclei_data)+1,
                        "Location_Center_X": centroid[0],
                        "Location_Center_Y": centroid[1],
                        "Location_Center_Z": 0,
                        "Mitocheck_Object_ID": objId
                        }
            nuclei_data.append(nucleus_data)
        
    nuclei_data = pd.DataFrame(nuclei_data)
    return nuclei_data

def segment_training_data(preproc_training_path, features_path, training_set_dat_path, save_path, cellpose_model):
    """
    saves nuclei location data in CellProfiler IdentifyPrimaryObjects format as csv file
    ie: ImageNumber, ObjectNumber, Location_Center_X, Location_Center_Y, Location_Center_Z
    """
    for plate_path in preproc_training_path.iterdir():
        for well_path in plate_path.iterdir():
            for frame_path in well_path.iterdir():
                for file_path in frame_path.iterdir():
                    segmented_save_dir = pathlib.Path(f"{save_path}/{plate_path.name}/{well_path.name}/{frame_path.name}")
                    print(f"Segmenting: {file_path}")
                    if segmented_save_dir.exists():
                        print("Movie has already been segmented!")
                    else:
                        try:
                            nuclei_data = get_nuclei_locations(file_path, features_path, training_set_dat_path, cellpose_model, plate_path.name, well_path.name, frame_path.name)
                            segmented_save_dir.mkdir(parents=True, exist_ok=False)
                            nuclei_data_path = pathlib.Path(f"{segmented_save_dir}/{plate_path.name}_{well_path.name}_{frame_path.name}.tsv")
                            nuclei_data.to_csv(nuclei_data_path, sep='\t')
                        except Exception as e:
                            print(e)


# ### Set Up CellPose

# In[35]:


use_GPU = core.use_gpu()
print('>>> GPU activated? %d'%use_GPU)
#logger_setup();


# ### Segment All Training Data

# In[36]:


load_path = pathlib.Path("../1.preprocess_data/labeled_frames_preprocessed/")
features_path = pathlib.Path("features/")
training_set_dat_path = pathlib.Path("../0.download_data/trainingset.dat")
save_path = pathlib.Path("segmented/")
cellpose_model = models.Cellpose(gpu=True, model_type='cyto')
segment_training_data(load_path, features_path, training_set_dat_path, save_path, cellpose_model)

