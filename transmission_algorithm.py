# -*- coding: utf-8 -*-
"""
Created on Thu Jul 18 14:14:18 2019

@author: Vijeta
"""

import pandas as pd
import numpy as np
import scipy as sp
from scipy import stats
import math
import re
import os
import link_to_cepac_in_and_out_files as link

def get_transmission_rate_multiplier(path):
    
    #%% calculations for transmission rate multiplier inside cohort
    
    def get_m_bar_tx_inside(path):
        
        # read data
        d_in = link.import_transmission_inputs_file(path)
        
        # calculate transition rate multiplier
        transition_rate_multiplier = {}
        transmission_rates = {}
        hiv_pop = {'neg': {}, 'pos': {}}
        for i in d_in:
            
            if np.isnan(d_in[i]['incidence']):
                transition_rate_multiplier[i] = 1
                continue
        
            # weighted average of transmission rate specific to risk group
            r_bar_dash = d_in[i]['incidence']*d_in[i]['n_hiv_neg']/d_in[i]['n_hiv_pos']
            
            # population specific transmission rates
            rate_ratio = np.matrix(d_in[i]['rates_attia']/d_in[i]['rates_attia'][len(d_in[i]['rates_attia']) - 1])
            r_dash = (np.matrix(r_bar_dash) / np.dot(rate_ratio, d_in[i]['dist_vl'])) * rate_ratio
        
            # calculate weighted average transition rate from HIV+ to HIV-,inside PC
            #r_bar_tx = 100 * (1 - math.exp(-1 * d_in[i]['Yearly incidence in MSM'])) * (d_in[i]['Number of HIV uninfected individuals (HRG size)'] / d_in[i]['Number of HIV infected individuals in primary cohort at t=0'])
            
            # transmission rate multiplier for inside group transmissions
            r_bar = np.dot(d_in[i]['rates_attia'], d_in[i]['dist_vl'])
            transition_rate_multiplier[i] = r_bar_dash/r_bar
            # transmission rates specific to HR group under consideration
            transmission_rates[i] = pd.DataFrame(r_dash)
            transmission_rates[i]['6'] = transmission_rates[i].iloc[0, 5]
            transmission_rates[i] = transmission_rates[i].astype('float')
            # hiv pop
            hiv_pop['neg'][i] = d_in[i]['n_hiv_neg']
            hiv_pop['pos'][i] = d_in[i]['n_hiv_pos']
            
        
        # return output
        return {'rates': transmission_rates, 'multiplier': transition_rate_multiplier, 
                'hiv_pop': hiv_pop}
    
    #%% calculations for transmission rate multiplier outside cohort
    
    def get_m_bar_tx_outside(path):
        # read data
        #d_in = get_meta_analysis_results(path)
        return False
    
    
    #%%
    # send out results
    m_bar_tx = {'Inside': get_m_bar_tx_inside(path),
                'Outside': get_m_bar_tx_outside(path)}
    
    return m_bar_tx

#%%
def get_percentage_decline(output_dict, inputs_req_from_user):
    
    # unroll the vars
    prep_uptake = inputs_req_from_user['PrEPCoverage']
    prep_efficacy = inputs_req_from_user['prep_efficacy'] 
    n_hiv_uninfected = inputs_req_from_user['CohortSize']
    prep_duration = inputs_req_from_user['PrEPDuration']
    p_sq_start = inputs_req_from_user['HIVmthIncidMale']
    
    # 
    if prep_uptake == 0.6 or prep_uptake == 60:
        print('')
    
    # take out transmission output from output_dict
    tx = {}
    inf = {}
    sus = {}
    inf_prob = {}
    for run in output_dict:
        if 'RunA' in run or 'A' in run:
            #tx['RunA'] = output_dict[run].loc[0:prep_duration, output_dict[run].shape[1] - 1].sum()
            tx['RunA'] = output_dict[run]['transmissions'].loc[0:prep_duration-1].sum()
            inf['RunA'] = output_dict[run]['infections'].loc[0:prep_duration-1].sum()
            sus['RunA'] = (n_hiv_uninfected * np.ones(output_dict[run]['infections'].loc[0:prep_duration-1].shape))
            sus['RunA'][1:] -= output_dict[run]['infections'].loc[0:prep_duration-2].cumsum()
            inf_prob['RunA'] = (output_dict[run]['infections'].loc[0:prep_duration-1])/sus['RunA']
        elif 'RunB' in run or 'B' in run:
            #tx['RunB'] = output_dict[run].loc[0:prep_duration, output_dict[run].shape[1] - 1].sum()
            tx['RunB'] = output_dict[run]['transmissions'].loc[0:prep_duration-1].sum()
            inf['RunB'] = output_dict[run]['infections'].loc[0:prep_duration-1].sum()
            sus['RunB'] = (n_hiv_uninfected * np.ones(output_dict[run]['infections'].loc[0:prep_duration-1].shape))
            sus['RunB'][1:] -= output_dict[run]['infections'].loc[0:prep_duration-2].cumsum()
            inf_prob['RunB'] = (output_dict[run]['infections'].loc[0:prep_duration-1])/sus['RunB']
        elif 'RunC' in run or 'C' in run:
            #tx['RunC'] = output_dict[run].loc[0:prep_duration, output_dict[run].shape[1] - 1].sum()
            tx['RunC'] = output_dict[run]['transmissions'].loc[0:prep_duration-1].sum()
            inf['RunC'] = output_dict[run]['infections'].loc[0:prep_duration-1].sum()
            sus['RunC'] = (n_hiv_uninfected * np.ones(output_dict[run]['infections'].loc[0:prep_duration-1].shape))
            sus['RunC'][1:] -= output_dict[run]['infections'].loc[0:prep_duration-2].cumsum()
            inf_prob['RunC'] = (output_dict[run]['infections'].loc[0:prep_duration-1])/sus['RunC']
    
    # now we have all the inputs required for calculation of percentage decline
    # in incidence due to community benefit
    if inputs_req_from_user['prep_usage_at_initialization'] in set(['y', 'Y', 'yes', 'Yes', 'YES']):
        p_int_start = ((1 - prep_uptake) * p_sq_start) + (prep_uptake * (1 - (1 - p_sq_start)**(1 - prep_efficacy)))
        i_sq_cumulative_agg = (1 - (1 - p_sq_start)**(prep_duration)) * n_hiv_uninfected
    elif inputs_req_from_user['prep_usage_at_initialization'] in set(['n', 'N', 'no', 'No', 'NO']):
        p_int_start = p_sq_start
        i_sq_cumulative_agg = inf['RunA']
    
    # function to calculate end month probability
    def calculate_end_p(val, denominator = False):
        p = val/n_hiv_uninfected
        p_per_month = 1 - np.power((1 - p), (1/prep_duration))
        if denominator:
            return p_per_month
        p_end = 2*p_per_month - p_int_start
    
        return p_end
    
    # old calculations
    step_1 = tx['RunA'] - tx['RunC'] # transmissions averted due to ind. benefit only
    step_2 = tx['RunA'] - tx['RunB'] # tx averted due to both benefits
    step_3 = calculate_end_p(inf['RunA'] - step_2) # p(inf) at t = end, if both benefits are present 
    step_4 = calculate_end_p(inf['RunA'] - step_1) # p(inf) at t = end, if only ind benefit was present
    step_5 = calculate_end_p(inf['RunA'] - step_1, True) # p(inf) per month
    percentage_decline = 100*(step_4 - step_3)/step_5
    
    # in revised template the calculation for prob at t=end has changed, as follows
    prob_ratio_at_zero = (inf_prob['RunB']/inf_prob['RunA']).loc[0]
    prob_sq_t = inf_prob['RunA'].loc[prep_duration-1]
    def calculate_average_prob(total_inf):
        p = total_inf/n_hiv_uninfected
        p_avg = 1 - np.power((1 - p), (1/prep_duration))
        
        return p_avg
    
    def calculate_end_p_new(p_avg_sq, p_avg_int):
        p_end = prob_ratio_at_zero * prob_sq_t + (2 * (p_avg_int - (prob_ratio_at_zero * p_avg_sq)))
        
        return p_end
    
    # calculate prob ratio
    step_1 = calculate_average_prob(inf['RunA']) # average prob in SQ
    step_2 = calculate_average_prob(inf['RunA'] - (tx['RunA'] - tx['RunC'])) # avrage prob in INV (only ind)
    step_3 = calculate_average_prob(inf['RunA'] - (tx['RunA'] - tx['RunB'])) # avrage prob in INV (both)
    step_4 = calculate_end_p_new(step_1, step_2) # p(inf)_t for INV with ind
    step_5 = calculate_end_p_new(step_1, step_3) # p(inf)_t for INV with both
    percentage_decline_new = 100 * (step_4 - step_5)/step_2
    
    # test
    if np.floor(1000 * percentage_decline_new) != np.floor(1000 * percentage_decline):
        print("")
        
    # debugging loop
    if tx['RunA'] >= inf['RunA']:
        print('gadbad')
    
    return percentage_decline_new


     

