# -*- coding: utf-8 -*-
"""
Created on Wed Jul  5 15:03:28 2019

@author: Vijeta
"""

import link_to_cepac_in_and_out_files as link
import visualization as viz
import adjustments_for_cepac_in_and_out_files as adjust
import numpy as np
import os

class CepacOutput:

    def __init__(self, path, sensitivity_module = False, transmission_module = False):
        '''
        # according to the active module, set path
        path = os.path.join(path, r'Input files')
        # next folder depends on module
        if transmission_module:
            path = os.path.join(path, r'Runs prepared for calculating percentage decline in incidence')
        elif sensitivity_module:
            path = os.path.join(path, r'Runs prepared for sensitivity analysis')
        '''
        # get list of directories in current path
        folder_list = os.listdir(path)
        d = {}
        f_idx = -1
        for folder in folder_list:
            f_idx += 1
            # set path
            float_path = os.path.join(path, folder_list[f_idx], 'results')
            # import all the data
            which_module = sensitivity_module*['sensitivity_module'] + transmission_module*['regression']
            d[folder] = self.get_structured_data(link.import_all_cepac_out_files(float_path, which_module[0]), sensitivity_module, transmission_module)

        # point the d dictionary to the relevant attribute
        self.output_data = d
        
        # if the transmission module is on, we'll need to read input files too
        if transmission_module:
            print('chan')
        
        return

    def get_structured_data(self, raw_data, sensitivity_module, transmission_module):
        
        # raw_data is basically a dictionaries within a dictionary
        # key1 = variable name (in the set of selected variables for S.A.)
        # key2 = value selected for the var in key1 for sensitivity analysis
        # therefore, raw_data[key1][key2] = output file
        
        # what we can do is create a dictionary for popstats outputs, which will
        # eventually be considered in ICER calculations and basic plots.
        # And, another dictionary for monthly/overall output data 
        d = {}
        d['popstats'] = raw_data.pop('popstats')
        if transmission_module:
            d['monthly'] = raw_data
        elif sensitivity_module:
            d['overall'] = raw_data
            
        
        return d
    
    def get_monthly_variation(self):
        
        
        
        return

def get_comparative_results(data):
    
    # check if input is dict
    # this data file should contain CEPAC results for base/int and sensitivity
    # analysis results for one or more variable considered in sens. ana.
    if not isinstance(data, dict):
        print('\n input data to get_comparative_results(data) function in processes_on_cepac_output.py, shold be a dictionary')
        return False
    
    # adjust the data we have
    data = adjust.do_adjustments_on_popstats(data)
    
    # with basecase and intervention values as reference calculate Icers
    for var in data:
        if var == 'Basecase and Intervention':
            continue
        var_df = data[var]
        var_val_len = len(var_df.index)
        delta_lm = var_df.loc[:, 'LMs_'].values() - (data['Basecase and intervention'].loc['basecase', 'LMs_'].values() * np.ones((var_val_len, 1)))  
        delta_qalm = var_df.loc[:, 'QALMs_'].values() - (data['Basecase and intervention'].loc['basecase', 'QALMs_'].values() * np.ones((var_val_len, 1)))  
        delta_c = var_df.loc[:, 'COST_'].values() - (data['Basecase and intervention'].loc['basecase', 'COST'].values() * np.ones((var_val_len, 1)))  
        if not all(delta_c == 0):
            icer = {'Without quality adjustments': np.zeros((var_val_len, 1)), 'Quality adjusted': np.zeros((var_val_len, 1))}
        else:
            icer = {'Without quality adjustments': delta_lm/delta_c, 'Quality adjusted': delta_qalm/delta_c}
        
    return





