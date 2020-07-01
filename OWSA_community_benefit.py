#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 17 13:49:08 2020

@author: vijetadeshpande
"""

import pandas as pd
import numpy as np
import scipy as sp
from scipy import stats
import math
import re
import os
import link_to_cepac_in_and_out_files as link
import cluster_operations as c_op
import TextFileOperations as t_op

#%% fixed variables

# user input
HORIZON = 120
strategies = ['30 in 36 months']#['30 in 36 months', '30 in 48 months', '40 in 36 months', '40 in 48 months']
var_list = ['PrEPAdherence', 'HIVtestFreqInterval', 'PrEPDroputPostThreshold']
base = r'/Users/vijetadeshpande/Downloads/MPEC/Brazil/Rio/1-way SA'

#%%

def community_benefit(run_A, run_B, HORIZON = 120):
    
    # few fixed parameters
    COHORT_SIZE = 10000000
    
    # Utils
    def calculate_average_prob(total_inf):
        p = total_inf/COHORT_SIZE
        p_avg = 1 - np.power((1 - p), (1/HORIZON))
        
        return p_avg    
    
    # calculate difference bet infection cases in SQ and INV
    step_1 = np.sum(run_A['transmissions'][0:HORIZON]) - np.sum(run_B['transmissions'][0:HORIZON])
    # calculate average monthly incidence probability in SQ
    step_2 = calculate_average_prob(np.sum(run_A['infections'][0:HORIZON]))
    # calculate average monthly incidence prob in INV
    step_3 = calculate_average_prob(np.sum(run_B['infections'][0:HORIZON]) - step_1)
    # difference in avg monthly prob
    step_4 = step_3 - step_2
    # monthly prob at time 't' for INV
    if  run_B['susceptibles'].sum() == 0:
        run_B['susceptibles'] = COHORT_SIZE * np.ones(len(run_B['susceptibles']))
        run_B['susceptibles'][1:] -= run_B['infections'].cumsum()[0:-1]
        
    inf_prob = np.divide(run_B['infections'], run_B['susceptibles'])[HORIZON - 1]
    step_5 = np.multiply(inf_prob, np.divide((np.sum(run_A['infections'][0:HORIZON]) - step_1), np.sum(run_A['infections'][0:HORIZON])))
    # percentage decrease in monthly probability at month t
    step_6 = np.divide((inf_prob - step_5), inf_prob)
    
    # incidence red
    percentage_decline = max(0, 100 * step_6)
    # coefficient
    coeff = -1 * HORIZON/(np.log(1 - step_6)) if percentage_decline > 0 else 10000
    
    #
    #output = {'Percentage reduction': percentage_decline, 'Reduction coefficient': coeff}
    
    # check
    #check = (((inf['RunA'] - tx['RunA']) < 0) or ((inf['RunB'] - tx['RunB']) < 0) or ((inf['RunC'] - tx['RunC']) < 0))
    #if check:
    #    print('wrong')
    """
    check = inf['RunA'] - tx['RunA']
    if check < 0:
        print('wrong')
    """
    
    return percentage_decline, coeff

#%%
 
for strategy in strategies:   
    #
    basepath = os.path.join(base, strategy)
    readbase = os.path.join(basepath, 'Measurement of community benefit')
    writebase = os.path.join(basepath, 'Final runs')
    sqpath = os.path.join(base, 'Common runs')
    readpaths = {}
    finalpaths = {}
    for var in var_list:
        float_name = 'OWSA_on var = ' + var
        readpaths[var] = os.path.join(readbase, float_name)
        finalpaths[var] = os.path.join(writebase, 'Final runs for var = %s'%(var))
    
    
    #%% 
    # collect and import all the ouputs
    cepac_outputs = {}
    cepac_outputs['status quo'] = link.import_all_cepac_out_files(os.path.join(sqpath, 'results'), module = 'regression')['SQ']
    community_ben = {}
    position = {}
    for var in readpaths:
        
        # collect output
        try:
            c_op.collect_output(readpaths[var])
        except:
            pass
        
        # read output
        cepac_outputs[var] = link.import_all_cepac_out_files(os.path.join(readpaths[var], 'results'), module = 'regression')
        
        # send to community benefit function 
        for file in cepac_outputs[var]:
            # calculate community benefit
            per_red, coeff = community_benefit(cepac_outputs['status quo'], cepac_outputs[var][file], HORIZON)
            coeff = max(coeff, 10**-8)
            community_ben[file] = {}
            community_ben[file]['percentage reduction'] = per_red
            community_ben[file]['reduction coefficient'] = coeff
            
            # read respective .in file
            filepath = os.path.join(readpaths[var], file) + '.in'
            float_in = link.read_cepac_in_file(filepath)
            
            # replace few values
            r_val_map = {'UseHIVIncidReduction': 1, 
                         'HIVIncidReductionStopTime': HORIZON, 
                         'HIVIncidReductionCoefficient': coeff}
            for r_var in r_val_map:
                #
                if not r_var in position:
                    position[r_var] = t_op.search_var(r_var, float_in)
                
                # replace value
                float_in = t_op.replace_values(r_var, r_val_map[r_var], float_in, position[r_var])
            
            # write the file
            varval = file.split('=')[1]
            addstr = 'OWSA_final_run_var=%s_val=%s'%(var, varval) + '.in'
            if not os.path.exists(finalpaths[var]): os.makedirs(finalpaths[var])
            savepath = os.path.join(finalpaths[var], addstr)
            link.write_cepac_in_file(savepath, float_in)
        
        # parallelize
        c_op.parallelize_input(finalpaths[var])
    
    
    
    
    