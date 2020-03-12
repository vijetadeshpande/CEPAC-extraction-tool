# -*- coding: utf-8 -*-
"""
Created on Wed Jul 24 14:53:38 2019

@author: Vijeta
"""
import transmission_algorithm as trans_algo
import os
from copy import deepcopy
import link_to_cepac_in_and_out_files as link
import pandas as pd

# initialize calculations for m_bar_tx
# prepare RunA, RunB and RunC templates
# loop over all the cities

def initialize_tx_module(path):
    
    # make input_files folder as current directory
    path = os.path.join(path, r'Input files')
    
    # TODO: following calculations might not me required if we are using dynamic transmisiosn module in RunA
    # step1: calculate m_bar_tx = transition rate multitplier
    m_bar_tx = trans_algo.get_transmission_rate_multiplier(path)
    
    # ste2: prepare RunA, RunB and RunC
    # output from import function is dictionary
    runs = link.import_all_cepac_in_files(path)
    k_runs = deepcopy(runs)
    
    # adjust key names
    for k in k_runs:
        if (str(k).endswith('RunA') or str(k).endswith('runA') or str(k).endswith('Run_A') or str(k).endswith('run_A')):
            runs['RunA'] = runs.pop(k)
        elif (str(k).endswith('RunB') or str(k).endswith('runB') or str(k).endswith('Run_B') or str(k).endswith('run_B')):
            runs['RunB'] = runs.pop(k)
        elif (str(k).endswith('RunC') or str(k).endswith('runC') or str(k).endswith('Run_C') or str(k).endswith('run_C')):
            runs['RunC'] = runs.pop(k)
    del k_runs
    
    #%% if we decide to import only basecase and intervention instead of 
    # run ABC, then we have to creat run c here!
    
    ##########################################################################
    
    #%%
    # TODO: following syeps to find indices of variables might not me required if we are using dynamic transmisiosn module in RunA
    # find location of m_bar_tx
    #multiplier_idx = runs['RunA'].loc[runs['RunA'].iloc[:, 0] == 'TransmissionRateMultiplier', :].index[0]
    #rates_on_art_idx = runs['RunA'].loc[runs['RunA'].iloc[:, 0] == 'TransmissionRateOnART', :].index.values[:-1]
    #rates_off_art_idx = runs['RunA'].loc[runs['RunA'].iloc[:, 0] == 'TransmissionRateOffART', :].index.values[:-1]
    multiplier_msm_idx = runs['RunA'].loc[runs['RunA'].iloc[:, 0] == 'TransmissionRiskMultiplier_T1', :].index[0]
    multiplier_msm_dist_idx = runs['RunA'].loc[runs['RunA'].iloc[:, 0] == 'TransmissionRiskDistribution', :].index[0]
    n_hiv_pos_idx = runs['RunA'].loc[runs['RunA'].iloc[:, 0] == 'DynamicTransmissionNumHIVPosHRG', :].index[0]
    n_hiv_neg_idx = runs['RunA'].loc[runs['RunA'].iloc[:, 0] == 'DynamicTransmissionNumHIVNegHRG', :].index[0]
    
    # ste3: loop over all the transmission rate multiplier
    for val in m_bar_tx['Inside']['multiplier']:
            
        # create a directory 
        if not os.path.exists(os.path.join(path, 'Runs prepared for calculating percentage decline in incidence')):
            new_path = os.path.join(path, 'Runs prepared for calculating percentage decline in incidence')
            os.makedirs(new_path)
            os.makedirs(os.path.join(new_path, val))
        
        if not os.path.exists(os.path.join(os.path.join(path, 'Runs prepared for calculating percentage decline in incidence'), val)):
            os.makedirs(os.path.join(os.path.join(path, 'Runs prepared for calculating percentage decline in incidence'), val))
            
        # define new path
        new_path = os.path.join(os.path.join(path, 'Runs prepared for calculating percentage decline in incidence'), val)
        
        # replace the index found above
        for run_label in runs:
            # replace values
            # transmission risk multiplier for msm
            runs[run_label].iloc[multiplier_msm_idx, 1:4] = m_bar_tx['Inside']['multiplier'][val]
            # 2. transmission risk distribution
            runs[run_label].iloc[multiplier_msm_dist_idx, 2:16] = 1
            runs[run_label].iloc[multiplier_msm_dist_idx + 2, 2:16] = 0
            
            #%% here we change n_hiv_pos and n_hiv_neg in warm-up run
            
            runs[run_label].iloc[n_hiv_pos_idx, 1] = m_bar_tx['Inside']['hiv_pop']['pos'][val]
            runs[run_label].iloc[n_hiv_neg_idx, 1] = m_bar_tx['Inside']['hiv_pop']['neg'][val]
            
            #%%
            # redefine new path
            float_path = os.path.join(new_path, val + '_' + run_label + r'.in')
        
            # create run files in the new path
            link.write_cepac_in_file(float_path, runs[run_label])
    
    return

def get_community_benefit(output_dict, path, inputs_req_from_user = {}):
    
    # input should be a dictionary of dataframes for results of RunA,B and C
    # check if input is dataframe
    if not isinstance(output_dict, dict):
        print('\nget_subset_of_out_file function in link_to_cepac_in_and_out_files.py file requires the input to be in pd.DataFrame format. Current input is not.')
        return False
    
    '''
    # supportive function
    def take_ip(var, msg, ip = 'float'):
        while var == None:
            try:    
                if ip == 'string':
                    var = str(input(msg))
                else: 
                    var = float(input(msg))
                break
            except ValueError:
                print('Invalid input, please try again')
        
        return var
    
    print_msg = {'prep_uptake': 'PrEP uptake (HIV test tab, cell K46): \n',
                 'prep_efficacy': 'PrEP efficacy (HIV test tab, cell O41): \n',
                 'n_hiv_uninfected': 'Number of HIV uninfected individuals in CEPAC run (Cohort size): \n',
                 'prep_duration': 'PrEP duration in months: \n',
                 'incidence_prob_sq_monthly': 'Probability of HIV incidence in status quo scenario (): \n',
                 'prep_usage_at_initialization': 'Do you want to assume that PrEP is already being used in the population (y/n): \n'}
    # take raw inputs from user
    if inputs_req_from_user == {}:
        print('\n\n================================================')
        print(('User is required enter few inputs for further calculations \n\n').upper())
        for var in print_msg:
            if var == 'prep_usage_at_initialization':
                inputs_req_from_user[var] = take_ip(None, print_msg[var], 'string')
            else:
                inputs_req_from_user[var] = take_ip(None, print_msg[var])
        
    '''
    # iputs required to calculate percentage decline
    if inputs_req_from_user == {}:
        inputs_req_from_user = link.extract_input_for_tx_rate_multiplier(path)
    
    #%%
    # TODO: following line is adjustment
    inputs_req_from_user["PrEPDuration"] = 60
    
    #%%
    
    # send values to the algorithm function
    percentage_decline = trans_algo.get_percentage_decline(output_dict, inputs_req_from_user)

    return percentage_decline, inputs_req_from_user
