# -*- coding: utf-8 -*-
"""
Created on Tue Nov 26 17:53:10 2019

@author: Vijeta

#%%

Create different A, B and C runs for different values of mentioned variables

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

# aux functions
def find_and_replace(df, var, val):
    df = deepcopy(df)
    
    # find var
    idx = df.loc[df.loc[:, 0] == var, :].index[0]
    col = df.loc[idx, :].dropna().index[1]
    # replace
    df.loc[idx, col] = val
    
    return df

if False:
    # import base A, B and C
    path = {"base_abc": r"C:\Users\Vijeta\Documents\Projects\Brazil PrEP\Transmission runs\Input files"}
    cepac_in = link.import_all_cepac_in_files(path["base_abc"])
    
    # which variables to change
    replace_val = {"PrEPCoverage": [0.1, 0.2, 0.3], "PrEPDuration": [24, 36, 48]}
    
    # replace values in b and c only
    for var1 in replace_val["PrEPCoverage"]:
        # get b and c run data
        run_b = deepcopy(cepac_in["B"])
        run_c = deepcopy(cepac_in["C"])
        
        # replce coverage
        run_b = find_and_replace(run_b, "PrEPCoverage", var1)
        run_c = find_and_replace(run_c, "PrEPCoverage", var1)
        
        # create directory
        dir_name = "Coverage - %d"%(var1*100)
        if not os.path.exists(os.path.join(path["base_abc"], dir_name)):
            path_save = os.path.join(path["base_abc"], dir_name)
            os.makedirs(path_save)
        
        for var2 in replace_val["PrEPDuration"]:
            
            # replace coverage time
            run_b = find_and_replace(run_b, "PrEPDuration", var2)
            run_c = find_and_replace(run_c, "PrEPDuration", var2) 
            
            # create directory
            dir_name = "Coverage time - %d"%(var2)
            if not os.path.exists(os.path.join(path_save, dir_name)):
                path_float = os.path.join(path_save, dir_name)
                os.makedirs(path_float)
            
            # save files
            path_b = os.path.join(path_float, "B.in")
            path_c = os.path.join(path_float, "C.in")
            link.write_cepac_in_file(path_b, run_b)
            link.write_cepac_in_file(path_c, run_c)


# read output and write final files       
path = {"output": r"C:\Users\Vijeta\Documents\Projects\Brazil PrEP\Transmission runs\Input files\Runs asked by Ken"}
dir_list = {"coverage": os.listdir(path["output"]), "coverage time": []}

cepac_out = {}
percentage_decline = {}
for p_coverage in dir_list["coverage"]:
    # create dictionary
    cepac_out[p_coverage] = {}
    percentage_decline[p_coverage] = {}
    
    # get all the subfolders
    dir_list["coverage time"] = os.listdir(os.path.join(path["output"], p_coverage))
    
    for p_coverage_time in dir_list["coverage time"]:
        p_res = os.path.join(path["output"], p_coverage, p_coverage_time, "results")
        
        # extract results
        cepac_out[p_coverage][p_coverage_time] = link.import_all_cepac_out_files(p_res, module = "regression")
        
        # calculate percentage decline
        percentage_decline[p_coverage][p_coverage_time], _ = dtm.get_community_benefit(cepac_out[p_coverage][p_coverage_time], os.path.join(p_res, ".."))

#%% create a set of final runs
for p_c in percentage_decline:
    for var in percentage_decline[p_c]:
        cepac_in = link.import_all_cepac_in_files(os.path.join(path["output"], p_c, var))
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
        val = {'x_cepac': {}, 'x_user_in': {'percentage_reduction': percentage_decline[p_c][var]}}
        cepac_in['intervention'] = link.calculations_for_depemdent_var(cepac_in['intervention'], dep_indep_var_set, val)
        
        # create a folder for writing in files
        final_run_path = os.path.join(path["output"], "Final runs")
        if not os.path.exists(final_run_path):
            os.makedirs(final_run_path)
            final_run_path = final_run_path
        
        # write files
        for case in cepac_in:
            float_path = os.path.join(final_run_path, case + "_" + p_c + "_" + var + r'.in')
            link.write_cepac_in_file(float_path, cepac_in[case])