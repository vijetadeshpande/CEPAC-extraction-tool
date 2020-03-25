# -*- coding: utf-8 -*-
"""
Created on Tue Jan  7 17:24:22 2020

@author: Vijeta
"""

import os
import re
from shutil import copy2
from shutil import rmtree

def parallelize_input(path):
    
    # get list of directories
    file_list = os.listdir(path)
    
    for file in file_list:
        if file == 'results':
            continue
        
        # create a folder
        folder_name = re.sub('.in', "", file)
        if not os.path.exists(os.path.join(path, folder_name)):
            os.makedirs(os.path.join(path, folder_name))
        
        # copy.in file in this folder
        src = os.path.join(path, file)
        dst = os.path.join(path, folder_name, file)
        copy2(src, dst)
        
        # delete previous file
        os.remove(src)
        
def collect_output(path):

    # get list of directories
    file_list = os.listdir(path)    
        
    # iterate through all paths
    for file in file_list:
        if '.DS_Store' in file:
            continue
        
        # collect .in file and .out file, respectively
        # .in
        src_path = os.path.join(path, file, file) + '.in'
        dst_path = os.path.join(path, file) + '.in'
        copy2(src_path, dst_path)
        
        #.out
        src_path = os.path.join(path, file, 'results', file) + '.out'
        if os.path.exists(src_path):
            dst_path = os.path.join(path, 'results', file) + '.out'
            # create dir for results 
            if not os.path.exists(os.path.join(path, 'results')):
                os.makedirs(os.path.join(path, 'results'))
            copy2(src_path, dst_path)
        
        # del old folder
        rmtree(os.path.join(path, file))
        

# mention path
#path = r'/Users/vijetadeshpande/Downloads/MPEC/Brazil/Rio/2-way SA/Final runs/results'
#parallelize_input(path)
#collect_output(path)