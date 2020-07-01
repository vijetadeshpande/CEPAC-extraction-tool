# -*- coding: utf-8 -*-
"""
Created on Fri Jan  3 12:53:46 2020

@author: Vijeta
"""
"""
THIS FILE CREATES INPUT FILES FOR MULTIPLE A, B AND C RUNS. THESE RUNS ARE 
USED TO CALCULATE PERCENTAGE DECLINATION IN THE INCIDENCE DUE TO COMMUNITY 
BENEFIT OF PrEP. IT BROADLY WORKS AS FOLLOWS:
    
NEW FOLDER FOR SQ AND iNTERVENTION CONTAINING ALL .in FILES FOR GIVEN VALUES
OF COVERAGE AND COVERAGE TIME VARIABLES IN CEPAC .in FILE = 
f(VALUES FOR COVERAGE AND COVERAGE TIME, PATH FOR BASE A, B, C FILES)

NOTE: THIS FILE MIGH WORK FOR INTERVENTIONS OTHER THAN PrEP BUT CURRENTLY IT 
ONLY WORKS FOR PrEP.
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


def write_abc(value_map, path_dict):
    
    # check if both inputs are dictionaries
    if not (isinstance(value_map, dict) or isinstance(path_dict, dict)):
        raise TypeError("Input needs to be in dictionary format.")
        return
    # check keys in the input dictionary
    for k in value_map:
        if not k in ["PrEPCoverage", "PrEPDuration"]:
            raise ValueError("Keys of the input dictionary should only contain PrEPCoverage and PrEPDuration")
            return
        
    # Lazyness encounter: remaning input because rest of the code was written with different name
    var_to_replace = value_map
    del value_map
    
    # create mesh grid for values
    val_to_replace = {}
    val_to_replace['PrEPCoverage'], val_to_replace['PrEPDuration'] = np.meshgrid(var_to_replace['PrEPCoverage'], var_to_replace['PrEPDuration'])
    
    # import the base files
    cepac_in = link.import_all_cepac_in_files(path_dict['input'])
    
    # find indices of the required variables
    idx = {}
    for k in var_to_replace:
        idx[k] = cepac_in['B'].loc[cepac_in['B'].loc[:, 0] == k, :].index.values
    
    # replace all the indices with respective values
    float_b = cepac_in['B']
    float_c = cepac_in['C']
    for row in range(len(val_to_replace['PrEPCoverage'])):
        #
        for col in range(val_to_replace['PrEPCoverage'].shape[1]):
            # don't need to create files for zero coverage, just use SQ results
            if float(val_to_replace["PrEPCoverage"][(row, col)]) == 0:
                continue
            #
            for var in var_to_replace: 
                float_b.loc[idx[var], 1:2] = val_to_replace[var][(row, col)]
                float_c.loc[idx[var], 1:2] = val_to_replace[var][(row, col)]
            
            # make new dir
            if not os.path.exists(path_dict['output']['intervention']):
                os.makedirs(path_dict['output']['intervention'])
            
            # name the input file
            path = path_dict['output']['intervention']
            # B
            name = "RunB_Coverage=%d, Duration=%d"%(100 * val_to_replace["PrEPCoverage"][(row, col)], val_to_replace["PrEPDuration"][(row, col)]) + r".in"
            float_path = os.path.join(path, name)
            link.write_cepac_in_file(float_path, float_b)
            # C
            name = "RunC_Coverage=%d, Duration=%d"%(100 * val_to_replace["PrEPCoverage"][(row, col)], val_to_replace["PrEPDuration"][(row, col)]) + r".in"
            float_path = os.path.join(path, name)
            link.write_cepac_in_file(float_path, float_c)
    
    # create a folder for status quo
    if not os.path.exists(path_dict['output']['status quo']):
        os.makedirs(path_dict['output']['status quo'])
    
    # write a status quo .in file in the stsus quo folder
    link.write_cepac_in_file(os.path.join(path_dict['output']['status quo'], 'SQ.in'), cepac_in['SQ'])

    return