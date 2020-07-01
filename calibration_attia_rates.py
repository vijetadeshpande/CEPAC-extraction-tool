#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 22 13:21:11 2020

@author: vijetadeshpande
"""

import numpy as np
import pandas as pd
import TextFileOperations as t_op
import link_to_cepac_in_and_out_files as link
import cluster_operations as c_op
from copy import deepcopy
import os
from scipy.stats import truncnorm

parameters = {'attia off ART': np.array([9.03, 8.12, 8.12, 4.17, 2.06, 0.16, 0, 62.56]),
              'attia on ART': np.array([9.03, 8.12, 8.12, 4.17, 2.06, 0.16, 0, 9.03]),
              'viral load distribution off ART': np.array([0.4219, 0.1956, 0.1563, 0.1201, 0.0825, 0.0235, 0.0000, 0.0000]),
              'viral load distribution on ART': np.array([0.0003, 0.0036, 0.0217, 0.0963, 0.3787, 0.4994, 0.0000, 0.0000]),
              'rio': {'viral load distribution': np.array([0.1141, 0.0554, 0.0580, 0.1027, 0.2987, 0.3709, 0.0000, 0.0000]),
                      'incidence': np.array([4.3, 1]),
                      'index positive': 16999,
                      'index negative': 94104,
                      'on ART': 0.73
                      },
              'salvador': {'viral load distribution': np.array([0.1226, 0.0593, 0.0607, 0.1032, 0.2928, 0.3614, 0.0000, 0.0000]),
                      'incidence': np.array([2.45, 1]),
                      'index positive': 3926,
                      'index negative': 41728,
                      'on ART': 0.71
                      },
              'manaus': {'viral load distribution': np.array([0.1268, 0.0612	, 0.0621, 0.1034, 0.2898, 0.3566, 0.0000, 0.0000]),
                      'incidence': np.array([1.4, 1]),
                      'index positive': 2828,
                      'index negative': 45937,
                      'on ART': 0.70
                      }
              }

# import all .in files
filepath = r'/Users/vijetadeshpande/Downloads/MPEC/Brazil/SA on control levers'
in_file = link.import_all_cepac_in_files(filepath)

# create folder for new in files
filepath_new = os.path.join(filepath, 'SA on testing rate') #'SA_percentage on '
if not os.path.exists(filepath_new):
    os.makedirs(filepath_new)
    
    
def SA_attia(factors):
    # loop over scale down scenarios
    replace_var = ['DynamicTransmissionNumTransmissionsHRG', 'TransmissionRiskMultiplier_T1', 'TransmissionRiskMultiplier_T2', 'TransmissionRiskMultiplier_T3', 'TransmissionRateOnART', 'TransmissionRateOffART']
    replace_val = {}
    for city in ['rio', 'salvador', 'manaus']:
        for k in factors:# this us scale down factor for Attia rates
            
            # multiply to attia
            attia_new = np.multiply(parameters['attia'], k)
            replace_val['TransmissionRateOnART'] = np.multiply(np.reshape(attia_new, (8, 1)), np.ones((8, 6)))
            replace_val['TransmissionRateOffART'] = np.multiply(np.reshape(attia_new, (8, 1)), np.ones((8, 6)))
            
            # calculate average transmission rate
            tx_avg = np.sum(np.multiply(attia_new, parameters[city]['viral load distribution']))
            replace_val['DynamicTransmissionNumTransmissionsHRG'] = tx_avg
            
            # calculate transmission rate calibrated to the incidence rate
            tx = np.multiply(parameters[city]['incidence'], np.divide(parameters[city]['index negative'], parameters[city]['index positive']))
            
            # calculate multiplier
            tx_mul = np.divide(tx, tx_avg)
            replace_val['TransmissionRiskMultiplier_T1'] = tx_mul[0]
            replace_val['TransmissionRiskMultiplier_T2'] = tx_mul[0]
            replace_val['TransmissionRiskMultiplier_T3'] = tx_mul[1]
            
            
            # replace values in .in file
            float_df = deepcopy(in_file[city])
            
            # replace the variables
            for var in replace_var:
                float_df = t_op.replace_values(var, replace_val[var], float_df)
                
            # save float_df
            filename = os.path.join(filepath_new, city + '_Attia scale down_' + str(k) + '.in')
            link.write_cepac_in_file(filename, float_df)
    
    # parallelize files
    c_op.parallelize_input(filepath_new)

def SA_treatment(values):
    # loop over scale down scenarios
    replace_var = ['DynamicTransmissionNumTransmissionsHRG', 'TransmissionRiskMultiplier_T1', 'TransmissionRiskMultiplier_T2', 'TransmissionRiskMultiplier_T3', 'TransmissionRateOnART', 'TransmissionRateOffART']
    replace_val = {}
    for city in ['rio', 'salvador', 'manaus']:
        for k in values:# this is  to vary % on ART
            
            # multiply to attia
            attia_on_ART = np.multiply(parameters['attia on ART'], 1)
            attia_off_ART = np.multiply(parameters['attia off ART'], 1)
            replace_val['TransmissionRateOnART'] = np.multiply(np.reshape(attia_on_ART, (8, 1)), np.ones((8, 6)))
            replace_val['TransmissionRateOffART'] = np.multiply(np.reshape(attia_off_ART, (8, 1)), np.ones((8, 6)))
            
            # calculate community viral load distibution
            on_art = np.multiply(k, parameters['viral load distribution on ART'])
            off_art = np.multiply((1-k), parameters['viral load distribution off ART'])
            community_vl = np.add(on_art, off_art)
            
            # calculate average transmission rate
            tx_avg = np.sum(np.multiply(parameters['attia off ART'], community_vl))
            replace_val['DynamicTransmissionNumTransmissionsHRG'] = tx_avg
            
            # calculate transmission rate calibrated to the incidence rate
            tx = np.multiply(parameters[city]['incidence'], np.divide(parameters[city]['index negative'], parameters[city]['index positive']))
            
            # calculate multiplier
            tx_mul = np.divide(tx, tx_avg)
            replace_val['TransmissionRiskMultiplier_T1'] = tx_mul[0]
            replace_val['TransmissionRiskMultiplier_T2'] = tx_mul[0]
            replace_val['TransmissionRiskMultiplier_T3'] = tx_mul[1]
            
            
            # replace values in .in file
            float_df = deepcopy(in_file[city])
            
            # replace the variables
            for var in replace_var:
                float_df = t_op.replace_values(var, replace_val[var], float_df)
                
            # save float_df
            filename = os.path.join(filepath_new, city + '_On treatment_' + str(k) + '.in')
            link.write_cepac_in_file(filename, float_df)
    
    # parallelize files
    c_op.parallelize_input(filepath_new)

def SA_acute(values):
    # loop over scale down scenarios
    replace_var = ['TransmissionRateOnART', 'TransmissionRateOffART']#, 'TransmissionRateOnART', 'TransmissionRateOffART']
    replace_val = {}
    for city in ['rio', 'salvador', 'manaus']:
        for k in values:
            
            # multiply to attia
            attia_new = parameters['attia']
            attia_new[len(attia_new)-1] = k
            replace_val['TransmissionRateOnART'] = np.multiply(np.reshape(attia_new, (8, 1)), np.ones((8, 6)))
            replace_val['TransmissionRateOffART'] = np.multiply(np.reshape(attia_new, (8, 1)), np.ones((8, 6)))
            
            # replace values in .in file
            float_df = deepcopy(in_file[city])
            
            # replace the variables
            for var in replace_var:
                float_df = t_op.replace_values(var, replace_val[var], float_df)
                
            # save float_df
            filename = os.path.join(filepath_new, city + '_Acute rate_' + str(k) + '.in')
            link.write_cepac_in_file(filename, float_df)
    
    # parallelize files
    c_op.parallelize_input(filepath_new)
    
def SA_testing(values):
    
    # variables to alter and their values
    replace_var = ['TransmissionRateOnART', 'TransmissionRateOffART', 'HIVtestBgAcceptRate'] #
    replace_val = {}
    
    # multiply to attia
    attia_new = np.multiply(parameters['attia'], 1)
    replace_val['TransmissionRateOnART'] = np.multiply(np.reshape(attia_new, (8, 1)), np.ones((8, 6)))
    replace_val['TransmissionRateOffART'] = np.multiply(np.reshape(attia_new, (8, 1)), np.ones((8, 6)))
    
    for city in ['rio', 'salvador', 'manaus']:
        for k in values:
            # change background testing rate
            replace_val['HIVtestBgAcceptRate'] = k
            
            # replace values in .in file
            float_df = deepcopy(in_file[city])
            
            # replace the variables
            for var in replace_var:
                float_df = t_op.replace_values(var, replace_val[var], float_df)
                
            # save float_df
            filename = os.path.join(filepath_new, city + '_Test accept rate_' + str(k) + '.in')
            link.write_cepac_in_file(filename, float_df)
    
    # parallelize files
    c_op.parallelize_input(filepath_new)
    
    return

def SA_tx_att_hrg(values):
    
    replace_var = ['TransmissionRateOnART', 'TransmissionRateOffART', 'DynamicTransmissionPropHRGAttrib']
    replace_val = {}
    for city in ['rio', 'salvador', 'manaus']:
        for k in values:# this is  to vary % on ART
            
            # multiply to attia
            attia_on_ART = np.multiply(parameters['attia on ART'], 1)
            attia_off_ART = np.multiply(parameters['attia off ART'], 1)
            replace_val['TransmissionRateOnART'] = np.multiply(np.reshape(attia_on_ART, (8, 1)), np.ones((8, 6)))
            replace_val['TransmissionRateOffART'] = np.multiply(np.reshape(attia_off_ART, (8, 1)), np.ones((8, 6)))
            
            # the percentage attributable to hrg
            replace_val['DynamicTransmissionPropHRGAttrib'] = k
            
            # replace values in .in file
            float_df = deepcopy(in_file[city])
            
            # replace the variables
            for var in replace_var:
                float_df = t_op.replace_values(var, replace_val[var], float_df)
                
            # save float_df
            filename = os.path.join(filepath_new, city + '_att_to_hrg_' + str(k) + '.in')
            link.write_cepac_in_file(filename, float_df)
    
    # parallelize files
    c_op.parallelize_input(filepath_new)
    
    return

def calculate_average_tx_rate(on_ART, parameters):
    
    avg_rate = np.zeros((len(on_ART), ))
    idx = -1
    for val in on_ART:
        idx += 1
        community_VL = np.multiply(val, parameters['viral load distribution on ART']) + np.multiply((1 - val), parameters['viral load distribution off ART'])
        weighted_avg = np.sum(np.multiply(community_VL, parameters['attia off ART']))
        avg_rate[idx] = weighted_avg
    
    return np.mean(avg_rate), np.std(avg_rate)


def take_samples(lower, upper, mu, sigma, sample_n = 1000000):
    # define distribution parameters
    a = (lower - mu)/sigma
    b = (upper - mu)/sigma
    
    # define distribution object
    dist = truncnorm(a, b, loc = mu, scale = sigma)
    
    # take samples
    samples = dist.rvs(sample_n) 
    
    return samples


def SA_testing_rate(values):
    
    replace_var = ['HIVtestBgAcceptRate']
    replace_val = {}
    for city in ['rio', 'salvador', 'manaus']:
        for k in values:# this is  to vary % on ART
            
            # dict of values
            replace_val['HIVtestBgAcceptRate'] = k
            
            # replace values in .in file
            float_df = deepcopy(in_file[city])
            
            # replace the variables
            for var in replace_var:
                float_df = t_op.replace_values(var, replace_val[var], float_df)
                
            # save float_df
            filename = os.path.join(filepath_new, city + '_testing_rate_' + str(k) + '.in')
            link.write_cepac_in_file(filename, float_df)
    
    # parallelize files
    c_op.parallelize_input(filepath_new)
    
    return
       
# sample on treatment values
#on_treat = take_samples(0.3, 0.9, 0.5, 0.2)
#mean_rate, sd_rate = calculate_average_tx_rate(on_treat, parameters)
     
# SA on scaling down attia rates


# SA on percentage on treatment
#values = [0.73, 0.71, 0.70]
#SA_treatment(values)

# SA on acute transmission rate
#values = [10, 15, 20, 25, 30, 40, 62.5]
#SA_acute(values)

# SA on testing parameter
#values = [0.2, 0.3, 0.4, 0.5]#, 0.007, 0.009, 0.01, 0.015]
#SA_testing(values)

# SA on transmissions attributable to HRG
#values = [0.7, 0.8]
#SA_tx_att_hrg(values)

# sa on background testing 
#values = [0.2, 0.3, 0.4, 0.5]
#SA_testing_rate(values)


#
#path = filepath_new
#c_op.parallelize_input(path, 2)
#c_op.collect_output(path)
link.export_output_to_excel(os.path.join(path, 'results'), os.path.join(path, 'results'), mod = 'treatment')

