#!/usr/bin/env python
# coding: utf-8

# # Aspera Training Movie Downloader
# ### Download training movies from IDR using the Aspera high-speed transfer client
# #### Import libraries

# In[2]:


import os
import pandas as pd


# #### Determine Labeled Data
# Save plate/well of feature data to `training_locations.tsv`

# In[3]:


#Read plates listed in features dataset to figure out which wells from which plates have labeled data
#Save these training locations into a file

def save_training_wells(features_path, save_path):
    data_list = []
    for plate in os.listdir(features_path):
        for well in os.listdir(features_path + plate + "/features"):
            data_list.append([plate, well])
    dataframe = pd.DataFrame(data_list, columns=['Plate', 'Well'])
    dataframe.to_csv(save_path, sep="\t")
    
features_path = "training_set/features/"
save_path = "training_locations.tsv"
save_training_wells(features_path, save_path)


# #### Download movies that have labels
# Use Aspera to download wells listed in `training_locations.tsv`

# In[4]:


def download_labeled_data(training_locations_path, screens_path, aspera_path, key_path, download_path):
    training_locations = pd.read_csv(training_locations_path, sep="\t")
    screens = pd.read_csv(screens_path, sep="\t", header=None)
    screens.columns = ["Plate", "Screen"]
    
    #download each well from IDR, if it is available on IDR
    for index, row in training_locations.iterrows():
        try:
            #example command: 
            """sudo /home/roshankern/.aspera/ascli/sdk/ascp
            -TQ -l500m -P 33001 -i /home/roshankern/Desktop/aspera/asperaweb_
            id_dsa.openssh idr0013@fasp.ebi.ac.uk:20150916-mitocheck-analysis/mitocheck/LT0001_02--ex2005_11_16--sp2005_02_17--tt17--c3/hdf5/00002_01.ch5 
            0.download_data/labeled_movies_ch5/"""
            
            #get location of screen
            screen_loc = screens.loc[screens['Plate'] == row['Plate'], 'Screen'].item().replace("../screens/", "").replace(".screen", "")
            
            well_path = "20150916-mitocheck-analysis/mitocheck/" + screen_loc + "/hdf5/00" + "{:03d}".format(row['Well']) + "_01.ch5"
            idr_location = "idr0013@fasp.ebi.ac.uk:" + well_path + " "
            
            os.makedirs(download_path + row['Plate'] + "/" + "{:03d}".format(row['Well']))
            command = "sudo " + aspera_path + " -TQ -l500m -P 33001 -i " + key_path + " " + idr_location + download_path + row['Plate'] + "/" + "{:03d}".format(row['Well'])
            print(command)
            os.system(command)
        except Exception as e: #some plates are not available on IDR
            print(e)


aspera_path = "/home/roshankern/.aspera/ascli/sdk/ascp"
key_path = "asperaweb_id_dsa.openssh"
os.makedirs("labeled_movies_ch5/", exist_ok=True)
download_path = "labeled_movies_ch5/"

training_locations_path = "training_locations.tsv"
screens_path = "idr0013-screenA-plates.tsv"

download_labeled_data(training_locations_path, screens_path, aspera_path, key_path, download_path)

