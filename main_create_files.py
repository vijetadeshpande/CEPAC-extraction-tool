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
city, horizon = 'Rio', int(120)
CITY_CODE = city[0] + str(10)
strategies = ['30 in 36 months']#['30 in 36 months', '30 in 48 months', '40 in 36 months', '40 in 48 months']
base = r'/Users/vijetadeshpande/Downloads/MPEC/Brazil/Rio/Long-acting PrEP' #r'/Users/vijetadeshpande/Downloads/MPEC/Brazil/Rio/Try this' #r'/Users/vijetadeshpande/Downloads/MPEC/Brazil/Salvador/1-way SA_S10/' # #
val_map_twsa = {'PrEPAdherence': [0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.80, 0.85], 'PrEPDroputPostThreshold': monthly_prob(np.array([0, 0.05, 0.1, 0.15, 0.20, 0.25]))}

# 
if city == 'Rio':
    min_adh, max_adh = 0.627, 0.692 #0.66
    min_drp, max_drp = 0.1464, 0.1939
elif city == 'Salvador':
    min_adh, max_adh = 0.590, 0.708 #0.649
    min_drp, max_drp = 0.1370, 0.2267
elif city == 'Manaus':
    min_adh, max_adh = 0.643, 0.727 #0.685
    min_drp, max_drp = 0.1328, 0.1978
    
#
#val_map_twsa = {'PrEPAdherence': np.linspace(min_adh, max_adh, 5), 'PrEPDroputPostThreshold': np.linspace(min_drp, max_drp, 5)}
val_map_twsa['PrEPAdherence'] = np.sort(np.concatenate((val_map_twsa['PrEPAdherence'], [min_adh, max_adh])))
val_map_twsa['PrEPDroputPostThreshold'] = np.sort(np.concatenate((val_map_twsa['PrEPDroputPostThreshold'], monthly_prob(np.array([min_drp, max_drp])))))


for strategy in strategies:
    #
    basepath = os.path.join(base, strategy, 'Basefiles')
    filepath = os.path.join(basepath, 'B.in')
    savepath = os.path.join(basepath, '..', 'Measurement of community benefit')#, 'Adherence_' + city + str(horizon))
    if not os.path.exists(savepath): os.makedirs(savepath)
    
    # value map
    val_maps = [{'PrEPAdherence': np.array([0.90, 0.95, 1.00])}, 
                {'HIVtestFreqInterval': np.array([6, 3, 1]).astype(int)},
                {'PrEPDroputPostThreshold': monthly_prob(np.array([0]))},
                {'InitAge': np.array([[252, 60], [288, 60], [324, 60], [360, 60], [396, 60]])}
               ]
    #val_maps = [{'DynamicTransmissionPropHRGAttrib': np.array([0.1, 0.3, 0.5, 0.7, 0.9])}]
    
    if True:
    # test OWSA
        for val_map in val_maps:
            
            #if 'HIVtestFreqInterval' in val_map.keys():
                #
            Rio_OWSA = AT.OneWaySA(filepath, savepath, val_map)
            Rio_OWSA.create_in_files()
            # parallel files for running it faster on cluster
            Rio_OWSA.parallelize(parallel = 1)
        
            # are there any other variables to replace?
            #replace_map = {}
            #Rio_OWSA.replace_val(replace_map)
    
    # test two-way SA
    #val_maps.pop('HIVtestFreqInterval')
    #Rio_TWSA = AT.TwoWaySA(filepath, savepath, val_map_twsa)
    #Rio_TWSA.create_in_files(parallel = 1)
