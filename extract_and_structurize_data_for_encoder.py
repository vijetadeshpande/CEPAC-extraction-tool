# -*- coding: utf-8 -*-
"""
Created on Mon Nov 18 14:36:52 2019

@author: Vijeta
"""

import link_to_cepac_in_and_out_files as link
import os
import re
import numpy as np
from sklearn.preprocessing import normalize

list_of_input_var = ["TransmissionRiskMultiplier_T3", "HIVIncidReductionCoefficient", "HIVIncidReductionStopTime",
               "HIVmthIncidMale", "PrepIncidMale", 
               "PrEPCoverage", "PrEPDuration", "PrEPShape"]

encoder_dimension = {"length": 1200, "breadth": 5}
decoder_dimension = {"length": 1200, "breadth": 3}
trajectory_len = 60
start_age = 381
cohort_size = 10000000

def get_weibull(coverage, duration, shape):
    # trajectory
    t = np.arange(1, trajectory_len+1)
    
    # weibull par and transition probability
    scale = -1*np.log(1 - coverage)/np.power(duration, shape)
    tp = 1 - np.exp((scale * np.power((t-1), shape, dtype = float)) - (scale * np.power(t, shape, dtype = float)))
    
    
    return tp

def select_input_subset(path, var = list_of_input_var):
    
    # get number of directories in the current folder
    folder_list = os.listdir(path)
    
    # define dictionary to collect all the subsetted data
    data_dict = {}
    
    # iterate over every folder
    for folder in folder_list:
        float_dict = link.import_all_cepac_in_files(os.path.join(path, folder))
        for k in float_dict:
            float_name = re.sub('.in', "", os.path.basename(os.path.normpath(k)))
            float_name = re.sub('cepac_run', "", float_name)
            data_dict[int(float_name)] = link.get_subset_of_in_file(float_dict[k], var)
        
    return data_dict

def select_output_subset(path):
    
    # get number of directories in the current folder
    folder_list = os.listdir(path)
    
    # define dictionary to collect all the subsetted data
    data_dict = {}
    float_dict = {}
    
    # iterate over every folder
    for folder in folder_list:
        new_pairs = link.import_all_cepac_out_files(os.path.join(path, folder, "results"), module = "regression")
        new_pairs.pop("popstats")
        float_dict.update(new_pairs)
    
    # convert keys into int type
    for k in float_dict:
        data_dict[int(k)] = float_dict[k]
        
    return data_dict

def expand_input_by_age(df, var):
    
    # TODO: following age groups are hard coded, but not in CEPAC excel in file
    # be careful
    tx_age = [0, 360, 468]
    inci_age =  np.multiply(12, [0, 18, 25, 30, 40, 46, 51, 55]) - np.ones((8))
    inci_age[0] = 0
    inci_age = inci_age.astype(int)
    
    if var in ["HIVmthIncidMale", "PrepIncidMale"]:
        data_in = df.loc[0, 2:].dropna().astype("float").values[:]
        set_i = inci_age
    else:
        data_in = df.loc[:, 3].astype("float")
        data_in = data_in.values[:]
        set_i = tx_age
        
    data_out = np.zeros((encoder_dimension["length"]))
    prev_i = 0
    idx = 0
    for i in set_i:
        if i == 0:
            continue
        # fill vector of len 1200
        data_out[prev_i:i] = data_in[idx]
        idx += 1
        prev_i = i
    data_out[prev_i: ] = data_in[idx]
        
    
    return data_out

def expand_output_by_age(df, var):
    
    #
    data_in = df.astype("float").values[0:trajectory_len]
    data_out = np.zeros((decoder_dimension["length"]))
    data_out[start_age - 1:start_age - 1 + trajectory_len] = data_in
    
    return data_out

def expand_input_by_function(df, var, shape = None, duration = None, stop_time = None):
    
    data_out = np.zeros((encoder_dimension["length"]))
    if var == "PrEPCoverage":
        shape = float(shape.loc[0, 1])
        duration = float(duration.loc[0, 1])
        coverage = float(df.loc[0, 1])
        tp = get_weibull(coverage, duration, shape)
        data_out[start_age - 1:start_age - 1 + trajectory_len] = tp
    else:
        coeff = float(df.loc[0, 1])
        stop_time = float(stop_time.loc[0, 1])
        # create a time vector
        time = np.zeros((encoder_dimension["length"]))
        # assume everyone starts at age = starting_age.
        # from that point, start simulation month count upto stop time
        sim_time = np.arange(1, stop_time)
        time[start_age-1:start_age-1 + len(sim_time)] = sim_time
        # once stop time is reached, it is min(stop_time, sim_month) in cepac
        # hence keep it stop time after stop time is reached
        time[start_age-1 + len(sim_time): ] = stop_time
        
        # calculate exponent
        exponent = time/coeff
        # and incidence reduction is by factor of e^(exponent) in CEPAC
        data_out = np.exp(-exponent)
    
    return data_out

def structurize_input_data(dict_in):
    
    # check that input is dictionary
    if not isinstance(dict_in, dict):
        return None
    
    # we want input to the encoder in [#var X 1] for each time step of each example
    # few variables in our input are only required to expand for each age 
    # while others need some coversion. Let's start with simple ones then 
    # we can move on to var which need conversion
    tensor_out = np.zeros((encoder_dimension["breadth"], encoder_dimension["length"], len(dict_in)))
    for example in dict_in:
        float_mat = np.zeros((encoder_dimension["breadth"],encoder_dimension["length"]))
        row_idx = 0
        for var in dict_in[example]:
            if var in ["PrEPDuration", "PrEPShape", "HIVIncidReductionStopTime"]:
                continue
            # Incidence wo PrEP, incidence with PrEP and tx multiplier only need age adjustments
            if var in ["HIVmthIncidMale", "PrepIncidMale", "TransmissionRiskMultiplier_T3"]:
                float_mat[row_idx, :] = expand_input_by_age(dict_in[example][var], var)
            else:
                if var == "PrEPCoverage":
                    float_mat[row_idx, :] = expand_input_by_function(dict_in[example][var], var, shape = dict_in[example]["PrEPShape"], duration = dict_in[example]["PrEPDuration"])
                else:
                    float_mat[row_idx, :] = expand_input_by_function(dict_in[example][var], var, stop_time = dict_in[example]["HIVIncidReductionStopTime"])
            row_idx += 1
        tensor_out[:, :, example] = float_mat
    
    # normalization
    for row in range(len(tensor_out[:, 0, 0])):
        if row in [2, 3]:
            continue
        else:
            max_r = np.max(tensor_out[row, :, :])
            min_r = np.min(tensor_out[row, :, :])
            tensor_out[row, :, :] = (tensor_out[row, :, :] - min_r * np.ones(tensor_out[row, :, :].shape))/(max_r - min_r)
    
    return tensor_out
    
def structurize_output_data(dict_in):
    
    # check that input is dictionary
    if not isinstance(dict_in, dict):
        return None
    
    # for now the shape of the output tesor will be as follows,
    # (#out_features, trajectory_len, examples)
    # for output, we only have var which need expansion by age
    tensor_out = np.zeros((decoder_dimension["breadth"], decoder_dimension["length"], len(dict_in)))
    for example in dict_in:
        float_mat = np.zeros((decoder_dimension["breadth"], decoder_dimension["length"]))
        row_idx = 0
        for var in dict_in[example]:
            if var in ["multiplier"]:
                continue
            float_mat[row_idx, :] = expand_output_by_age(dict_in[example][var], var)
            row_idx += 1
        #%%
        # adjustment if there's no output of susceptible
        x = cohort_size * np.ones((decoder_dimension["length"]))
        x -= float_mat[0, :]
        x[start_age - 1 + trajectory_len: ] = x[start_age - 1 + trajectory_len - 1]
        float_mat[2, :] = x
        #%%
        tensor_out[:, :, example] = float_mat
            
    # normalization
    for row in range(len(tensor_out[:, 0, 0])):
        max_r = np.max(tensor_out[row, :, :])
        min_r = np.min(tensor_out[row, :, :])
        tensor_out[row, :, :] = (tensor_out[row, :, :] - min_r * np.ones(tensor_out[row, :, :].shape))/(max_r - min_r)

    return tensor_out
    