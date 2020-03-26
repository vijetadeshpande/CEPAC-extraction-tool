#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 26 10:53:21 2020

@author: vijetadeshpande
"""

import AnalysisTasks as AT
import DependentVarList as DepList

base_in_file_path = r'/Users/vijetadeshpande/Downloads/MPEC/Brazil/TEST CODE/Rio.in'
save_path = r'/Users/vijetadeshpande/Downloads/MPEC/Brazil/TEST CODE/'

# value map
val_map = {'PrEPEfficacy': [0, 0.1, 0.2, 0.3, 0.4], 'PrEPDuration': [12, 24, 36, 48, 60]}

# check if the variables selected need data not present in .in file
# e.g. If we want to change efficacy, 
#       1. Efficacy var is not present in .in file
#       2. PrEPIncid named variable in CEPAC sheet changes if we change efficacy
#       3. There, we want to change PrEPIncid, which needs valu of efficacy. But, efficacy is not present in .in file
#       4. take such data from user

if False:
    # test OWSA
    Rio_OWSA = AT.OneWaySA(base_in_file_path, save_path, val_map)
    Rio_OWSA.create_in_files(parallel = 2)

# test two-way SA
Rio_TWSA = AT.TwoWaySA(base_in_file_path, save_path, val_map)
Rio_TWSA.create_in_files(parallel = 5)
