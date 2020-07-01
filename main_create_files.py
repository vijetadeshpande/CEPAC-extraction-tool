#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 26 10:53:21 2020

@author: vijetadeshpande
"""

import AnalysisTasks as AT
import DependentVarList as DepList
import os
import numpy as np

#
def monthly_prob(prob_y):
    rate_y = -1 * np.log(1 - prob_y)
    rate_m = rate_y/12
    prob_m = 1 - np.exp(-1 * rate_m)
    
    return prob_m


#
city, horizon = 'Manaus', int(120)
CITY_CODE = city[0] + str(int(horizon/12))
strategies = ['30 in 36 months']#['30 in 36 months', '30 in 48 months', '40 in 36 months', '40 in 48 months']
base = r'/Users/vijetadeshpande/Downloads/MPEC/Brazil/Rio/2-way SA_surf' #r'/Users/vijetadeshpande/Downloads/MPEC/Brazil/Rio/1-way SA/'
val_map_twsa = {'PrEPAdherence': [0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.80, 0.86], 'PrEPDroputPostThreshold': [0, 0.05, 0.1, 0.15, 0.20, 0.25]}

for strategy in strategies:
    #
    basepath = os.path.join(base, strategy, 'Basefiles')
    filepath = os.path.join(basepath, 'B.in')
    savepath = os.path.join(basepath, '..', 'Measurement of community benefit')#, 'Adherence_' + city + str(horizon))
    if not os.path.exists(savepath): os.makedirs(savepath)
    
    # value map
    val_maps = [{'PrEPAdherence': np.array([0.5, 0.6, 0.7, 0.8, 0.86])}, 
                 {'HIVtestFreqInterval': np.array([6, 3, 1]).astype(int)},
                 {'PrEPDroputPostThreshold': monthly_prob(np.array([0, 0.10, 0.20, 0.25]))}]
    
    #if False:
    # test OWSA
    #for val_map in val_maps:
        
        #if 'HIVtestFreqInterval' in val_map.keys():
            #
        #Rio_OWSA = AT.OneWaySA(filepath, savepath, val_map)
        #Rio_OWSA.create_in_files()
        # parallel files for running it faster on cluster
        #Rio_OWSA.parallelize(parallel = 1)
    
        # are there any other variables to replace?
        #replace_map = {}
        #Rio_OWSA.replace_val(replace_map)
    
    # test two-way SA
    #val_maps.pop('HIVtestFreqInterval')
    Rio_TWSA = AT.TwoWaySA(filepath, savepath, val_map_twsa)
    Rio_TWSA.create_in_files(parallel = 1)
