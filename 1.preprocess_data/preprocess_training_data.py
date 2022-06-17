#!/usr/bin/env python
# coding: utf-8

# # Training Movie Preprocessor
# ### Preprocesses Training Movies from Aspera IDR downloader
# 
# #### Import libraries

# In[1]:


import imagej
import pandas as pd
import pathlib
from IPython.utils.io import capture_output
import os

import PyBaSiC.pybasic as pybasic
import numpy as np

import skimage


# ### Determine what frames are labled from each training movie

# In[2]:


#Read plates listed in features dataset to figure out which frames from each movie have training data
#Save these training locations into training_frames file

def save_training_wells(traingset_path, save_path):
    data_list = []
    with open(traingset_path) as labels_file:
        for line in labels_file:
            if ".tif" in line: #get plate/well/frame for training data
                plate = line.strip()[:9]
                well = line.strip()[14:17]
                time = line.strip()[29:33]
                frame = int(int(time)/30 + 1)
                data_list.append([plate, well, frame])
                    
    dataframe = pd.DataFrame(data_list, columns=['Plate', 'Well', 'Frame'])
    dataframe.to_csv(save_path, sep="\t")

features_path = "../0.download_data/trainingset.dat"
save_path = "training_frames.tsv"
save_training_wells(features_path, save_path)


# ### Load image data given plate, well, frame

# In[3]:


#return movie data for particular plate/well
def load_training_movie_data(ij, parent_dir, plate, well):
    #create absolute path for ImageJ to load CH5 from
    parent_path = pathlib.Path(parent_dir).absolute().resolve()
    movie_file_path = f"{plate}/{well}/00{well}_01.ch5"
    movie_path = parent_path.joinpath(movie_file_path)
    
    #imagej prints lots of output that isnt necessary, unfortunately some will still come through
    with capture_output():
        movie_path = str(movie_path)
        jmovie = ij.io().open(movie_path)
        movie = ij.py.from_java(jmovie)
        movie_arr = movie.values[-94:, :, :, 0]
        return movie_arr


# #### PyBaSiC Illumination correction as described in http://www.nature.com/articles/ncomms14836

# In[4]:


def pybasic_illumination_correction(brightfield_images):
    
    flatfield, darkfield = pybasic.basic(brightfield_images, darkfield=True)
    
    baseflour = pybasic.background_timelapse(
        images_list = brightfield_images, 
        flatfield = flatfield, 
        darkfield = darkfield
    )
    
    brightfield_images_corrected_original = pybasic.correct_illumination(
        images_list = brightfield_images, 
        flatfield = flatfield, 
        darkfield = darkfield,
        background_timelapse = baseflour
    )
    
    #convert corrected images to numpy array, normalize, and convert to uint8
    brightfield_images_corrected = np.array(brightfield_images_corrected_original)
    brightfield_images_corrected[brightfield_images_corrected<0] = 0 #make negatives 0
    brightfield_images_corrected = brightfield_images_corrected / np.max(brightfield_images_corrected) # normalize the data to 0 - 1
    brightfield_images_corrected = 255 * brightfield_images_corrected # Now scale by 255
    corrected_movie = brightfield_images_corrected.astype(np.uint8)
    
    return corrected_movie


# ### Preprocess all training movies and save frames that have labeled data

# In[5]:


def preprocess_training_movies(ij, training_frames_path, downloads_dir, save_dir):
    training_locations = pd.read_csv(training_frames_path, sep="\t", dtype=object)
    
    #download each well from IDR, if it is available on IDR
    for index, row in training_locations.iterrows():
        plate = row["Plate"]
        well = row["Well"]
        frame = row["Frame"]
        print(f"\nPreprocessing {plate} {well} {frame}")
        try:
            save_path = pathlib.Path(f"{save_dir}{plate}/{well}/")
            if not save_path.exists():
                #determine what frames in the movie are labeled
                plate_well_frames = training_locations[(training_locations["Plate"]==row["Plate"]) & (training_locations["Well"]==row["Well"])]
                frame_nums = plate_well_frames["Frame"].tolist()
                print(f"Labeled frames: {frame_nums}")
                
                original_movie = load_training_movie_data(ij, downloads_dir, row["Plate"], row["Well"])
                corrected_movie = pybasic_illumination_correction(original_movie)
                
                #save all frames that have already had illumination correction
                for frame_num in frame_nums:
                    try:
                        labeled_frame = corrected_movie[int(frame_num)-1]
                        frame_dir_save_path = save_path.joinpath(f"{frame_num}")
                        frame_dir_save_path.mkdir(parents=True, exist_ok=True)
                        frame_save_path = frame_dir_save_path.joinpath(f"{plate}_{well}_{frame_num}.tif")
                        skimage.io.imsave(frame_save_path, labeled_frame)
                    except Exception as e:
                        print(e)
            else:
                print("Movie has already been preprocessed!")
        except Exception as e:
            print(e)
    

ij = imagej.init('Fiji.app')
#imagej init sets directory to /Fiji.app so have to go back a directory :/
os.chdir("..")

training_frames_path = "training_frames.tsv"
downloads_dir = "../0.download_data/labeled_movies_ch5/"
save_dir = "labeled_frames_preprocessed/"

test = preprocess_training_movies(ij, training_frames_path, downloads_dir, save_dir)

