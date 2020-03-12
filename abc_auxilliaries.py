# -*- coding: utf-8 -*-
"""
Created on Wed Jan 15 15:19:38 2020

@author: Vijeta
"""

import numpy as np
import link_to_cepac_in_and_out_files as link
import os
import pandas as pd
import re
import transmission_algorithm as tx_algo
import matplotlib.pyplot as plt
import seaborn as sb
from copy import deepcopy
import math
#from joblib import Parallel, delayed
import multiprocessing

# aux functions
def get_digit_for_file_name(key, ref):
    
    # dictionary is mutable
    ref = deepcopy(ref)
    
    # expand string
    names = key.split()
    val = {}
    for i in range(len(names)):
        names[i] = re.sub(",", "", names[i])
        if "Coverage" in names[i]:
            val["PrEPCoverage"] = int(names[i].split("=")[1])
        else:
            val["PrEPDuration"] = int(names[i].split("=")[1])
    
    # serach values in ref
    idx = {}
    ref["PrEPDuration"] = np.floor(ref["PrEPDuration"]).astype("int")
    ref["PrEPCoverage"] = np.floor(ref["PrEPCoverage"] * 100).astype("int")
    for i in val:
        idx[i] = np.where(ref[i] == val[i])[0]
    idx = (idx["PrEPCoverage"][0])*len(ref['PrEPDuration']) + idx["PrEPDuration"][0]
    
    return idx

def split_file_name(name):
    # expand string
    names = name.split()
    val = {}
    for i in range(len(names)):
        names[i] = re.sub(",", "", names[i])
        if "Coverage" in names[i]:
            val["PrEPCoverage"] = int(names[i].split("=")[1])
        else:
            val["PrEPDuration"] = int(names[i].split("=")[1])
    
    return val

def get_coverage_level_from_file_name(key):
    
    return split_file_name(key)["PrEPCoverage"]

def get_coverage_time_from_file_name(key):
    
    return split_file_name(key)["PrEPDuration"]
    
    
    
