# -*- coding: utf-8 -*-
"""
Created on Wed Jul 24 12:02:40 2019

@author: Vijeta



#%%

This file can

1. create runs A, B and C from base files
2. If results are present, it can calculate percentage declination and 
create final set of runs
3. if final set of runs have results, it can plot the results

#%%

"""

from processes_on_cepac_input import CepacInput
from processes_on_cepac_output import CepacOutput
from processes_on_cepac_output import get_comparative_results
from ProjectDetails import ProjectDetails
import dynamic_transmissions_module as dtm
import os 
import pandas as pd
import visualization as viz
import link_to_cepac_in_and_out_files as link
from copy import deepcopy


# get current path
tool_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..'))

# create a project object and treat it as a root node
brazil_prep = ProjectDetails(title="brazil prep", aim="CEA of prep for MSM", country="Brazil")

# saving path names for respective folders
path_names = {'sensitivity': os.path.join(parent_dir, 'Sensitivity runs'),
              'transmission': os.path.join(parent_dir, 'Transmission runs')}

# =============================================================================
# # required input files
req_in = {'transmission_rate_multiplier_required_inputs.xlsx'}
# req_in = {}
# =============================================================================

# a function to check if all the folders sent to or supposed to be sent to
# cluster have the results folder or not
def does_results_exist(path):
    folder_list = os.listdir(path)
    for i in folder_list:
        float_path = os.path.join(path, i)
        if not os.path.exists(os.path.join(float_path, 'results')):
            print('Results folder is missing in following path:')
            print(float_path)
            return False
    return True

# check if directories exits for respective operations
which_operation_to_perform = {'prepare_tx_runs': False, 'analyze_tx_runs': False, 'analyze_final_runs': False}
if os.path.exists(path_names['transmission']):
    if os.path.exists(os.path.join(path_names['transmission'], r'Input files')):
        if (req_in & set(os.listdir(os.path.join(path_names['transmission'], r'Input files')))) == req_in:
            if not os.path.exists(os.path.join(path_names['transmission'], r'Input files', r'Runs prepared for calculating percentage decline in incidence')):
                which_operation_to_perform['prepare_tx_runs'] = True
            else:
                if os.path.exists(os.path.join(path_names['transmission'], r'Input files', r'Final runs after calculating percenatge decline in incidence')):
                    if does_results_exist(os.path.join(path_names['transmission'], r'Input files', r'Final runs after calculating percenatge decline in incidence')):
                        which_operation_to_perform['analyze_final_runs'] = True
                else:
                    path = os.path.join(path_names['transmission'], r'Input files', r'Runs prepared for calculating percentage decline in incidence')
                    if does_results_exist(path):
                        which_operation_to_perform['analyze_tx_runs'] = True
        else:
            print('\nThe folder, Input files, is missing one or more of following required files:')
            print(req_in)
    else:
        print('folder, Input files, should exists for this tool to work. Path should be as follows:')
        print(os.path.join(path_names['transmission'], r'Input files'))
else:
    print('folder, Sensitivity runs, should exists for this tool to work. Path should be as follows:')
    print(os.path.join(parent_dir, 'Transmission runs'))


#%% prepare runs or extract results

if which_operation_to_perform['prepare_tx_runs']:
    all_runs = CepacInput(path_names['transmission'], transmission_module = True)

if which_operation_to_perform['analyze_tx_runs']:

    tx_out_object = CepacOutput(os.path.join(path_names['transmission'], r'Input files', r'Runs prepared for calculating percentage decline in incidence'), transmission_module = True)
    tx_data = tx_out_object.output_data

    # get the percentage decline values
    percentage_decline = {}
    inputs_req_from_user = {}
    for folder in tx_data:
        percentage_decline[folder], inputs_req_from_user = dtm.get_community_benefit(tx_data[folder]['monthly'], path)# inputs_req_from_user)
        
#%% plot transmission results
    """
    plot_path = os.path.join(path_names['transmission'], r'Results and plots')
    # create directory
    if not os.path.exists(plot_path):
        os.makedirs(plot_path)
        
    if not os.path.exists(os.path.join(plot_path, r'Dynamic transmissions and percentage decline')):
        os.makedirs(os.path.join(plot_path, r'Dynamic transmissions and percentage decline'))
        plot_path = os.path.join(plot_path, r'Dynamic transmissions and percentage decline')
        viz.plot_transmission_results(tx_data, percentage_decline, plot_path, path_names)
    else:
        viz.plot_transmission_results(tx_data, percentage_decline, plot_path, path_names)

#%% plot longitidinal histories

    long_data = {}
    folder_list = os.listdir(path)
    for i in folder_list:
        float_path = os.path.join(path, i, 'results')
        if not os.path.exists(float_path):
            print('Results folder is missing in following path:')
            print(float_path)
        else:
            long_data[i] = link.import_all_cepac_out_files(path = float_path, extensions = [r'\*.txt'])
    """
#%% create a set of final runs
    for var in percentage_decline:
        cepac_in = link.import_all_cepac_in_files(os.path.join(path, var))
        float_in = deepcopy(cepac_in)
        # adjustments
        for run in cepac_in:
            if 'RunC' in run or 'C' in run:
                float_in.pop(run)
            elif 'RunA' in run or 'A' in run:
                float_in['beasecase'] = float_in.pop(run)
            elif 'RunB' in run or 'B' in run:
                float_in['intervention'] = float_in.pop(run)
                
        del cepac_in
        cepac_in = float_in
        del float_in
    
        
        # here we want to change the values percenatg decline
        # but, reduction coefficient is dependent on this values. hence,
        # if we change the value of percenatge decline, value of reduction 
        # coefficient should also change
        # therefore, final dependent variable in this case is red_coeff
        dep_indep_var_set = {'y': 'HIVIncidReductionCoefficient', 
                             'x_cepac': ['HIVIncidReductionStopTime'],
                             'x_user_in': ['percenatge_reduction']}
        
        # change the value in cepac_input file
        val = {'x_cepac': {}, 'x_user_in': {'percentage_reduction': percentage_decline[var]}}
        cepac_in['intervention'] = link.calculations_for_depemdent_var(cepac_in['intervention'], dep_indep_var_set, val)
        
        # create a folder for writing in files
        final_run_path = os.path.join(path_names['transmission'], r'Input files', r'Final runs after calculating percenatge decline in incidence')
        if not os.path.exists(final_run_path):
            os.makedirs(final_run_path)
            final_run_path = os.path.join(final_run_path, var)
            os.makedirs(final_run_path)
        elif not os.path.exists(os.path.join(final_run_path, var)):
            final_run_path = os.path.join(final_run_path, var)
            os.makedirs(final_run_path)
        else:
            final_run_path = os.path.join(final_run_path, var)
        
        # write files
        for case in cepac_in:
            float_path = os.path.join(final_run_path, case + r'.in')
            link.write_cepac_in_file(float_path, cepac_in[case])
       
if which_operation_to_perform['analyze_final_runs']:
    
#%% plots and analysis on cepac output for final runs
    final_out_object = CepacOutput(os.path.join(path_names['transmission'], r'Input files', r'Final runs after calculating percenatge decline in incidence'), transmission_module = True)
    final_data = final_out_object.output_data  
    viz.plot_after_transmission_results(final_data, path_names)
