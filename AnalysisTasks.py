#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 23 13:05:30 2020

@author: vijetadeshpande
"""

import os
import sys
import pandas as pd
import link_to_cepac_in_and_out_files as link
import TextFileOperations as top
import numpy as np
from copy import deepcopy

class FileChange:
    def __init__(self, filepath, value_map):
        # check if value map is a dictionary
        if not isinstance(value_map, dict):
            raise TypeError('The input value_map must be a python dictionary')
            return
        
        self.base_in_file = link.read_cepac_in_file(filepath)
        self.var_list = np.array(value_map.keys())
        self.value_map = value_map
    
    def replace_values(self, var, val, in_file):
        
        # avoid mutability
        in_file = deepcopy(in_file)
        
        in_file = top.replace_values(var, val, in_file)
        
        return in_file
        