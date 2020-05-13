# -*- coding: utf-8 -*-
"""
Created on Tue Jan  7 17:24:22 2020

@author: Vijeta
"""

import os
import re
from shutil import copy2
from shutil import rmtree

ignore_list = ['results', '.DS_Store', 'job.info']

def parallelize_input(path, parallel = 1):
    
    # get list of directories
    file_list = os.listdir(path)
    
    # using numbers to name the folder
    folder_name = 0
    file_count = 0
    for file in file_list:
        if file in ignore_list:
            continue
        
        # increase file count and change folder name accordingly
        file_count += 1
        if file_count > parallel:
            file_count = 1
            folder_name += 1
        
        # create a folder
        if not os.path.exists(os.path.join(path, str(folder_name))):
            os.makedirs(os.path.join(path, str(folder_name)))
        
        # copy.in file in this folder
        src = os.path.join(path, file)
        dst = os.path.join(path, str(folder_name), file)
        copy2(src, dst)
        
        # delete previous file
        os.remove(src)
        
def collect_output(path, parallel = 1):

    # get list of directories
    folder_list = os.listdir(path)    
        
    # iterate through all paths
    for folder in folder_list:
        # ignore files
        if folder in ignore_list:
            continue
        
        # get list of '.in' files in the current folder and loop over it
        file_list = os.listdir(os.path.join(path, folder))
        for file in file_list:
            # ignore files
            if file in ignore_list:
                continue
            
            # collect .in file and .out file, respectively
            # .in
            src_path = os.path.join(path, folder, file)
            dst_path = os.path.join(path, file)
            copy2(src_path, dst_path)
            
            #.out
            file = file[:-3] + '.out'
            src_path = os.path.join(path, folder, 'results', file) #+ '.out'
            if os.path.exists(src_path):
                dst_path = os.path.join(path, 'results', file) #+ '.out'
                # create dir for results 
                if not os.path.exists(os.path.join(path, 'results')):
                    os.makedirs(os.path.join(path, 'results'))
                copy2(src_path, dst_path)
            
        # del old folder
        rmtree(os.path.join(path, folder))
        

# mention path
#path = r'/Users/vijetadeshpande/Downloads/MPEC/Brazil/Scaling down transmission rates/new_files'
#parallelize_input(path, 2)
#collect_output(path)