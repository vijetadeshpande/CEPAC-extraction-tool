# -*- coding: utf-8 -*-
"""
Created on Fri Nov  1 13:24:00 2019

@author: Vijeta


#%%

1. This file can create input files for 2-way sensitivity analysis, currently,
(PrEPCoverage and PrEPCoverage time) vs Percentage declination in incidence

2. Extract and read the output
3. PLot theat map for the results

#%%

"""

import numpy as np
import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from copy import deepcopy
import abc_input_cov_covtime as abc_input
import abc_output_cov_covtime as abc_output
import abc_final
import cluster_operations as c_op
import link_to_cepac_in_and_out_files as link
import abc_compare_old_new as abc_compare

#%% Input reading and file creation


# path to import in files
path_dict = {}
path_dict['input'] = r"C:\Users\Vijeta\Documents\Projects\Brazil PrEP\Transmission runs\CURRENT ANALYSIS\February\Proud trial\New CEPAC\Acute phase for 1 month\After correction (Acutr phase 2 months)"
path_dict['output'] = {}
path_dict['output']['intervention'] = os.path.join(path_dict["input"], "Positive coverage runs")
path_dict['output']['status quo'] = os.path.join(path_dict["input"], "Status quo")

# find and replace following variable
var_to_replace = {'PrEPCoverage': np.array([1]), 'PrEPDuration': np.array([1])}
#var_to_replace = {'PrEPCoverage': np.array([0.01, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5, 0.6]), 'PrEPDuration': np.array([24, 36, 48, 60])}
#{'PrEPCoverage': np.array([0, 0.07, 0.15, 0.22, 0.30]), 'PrEPDuration': np.array([6, 19, 33, 46, 60])} 
#{'PrEPCoverage': np.array([0.01, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5, 0.6]), 'PrEPDuration': np.array([24, 36, 48, 60])} # 

# check which path exists
if os.path.exists(os.path.join(path_dict['input'], 'Final runs')):
    # collect parallelized output
    c_op.collect_output(os.path.join(path_dict['input'], 'Final runs'))
    
    # analyzze final runs
    final_path = os.path.join(path_dict['input'], 'Final runs', 'results')
    sq_path = os.path.join(path_dict['output']['status quo'], 'results')
    abc_final.analyze_final_output(final_path, sq_path)
    
    # extract output in excel
    link.export_output_to_excel(final_path, final_path)

elif os.path.exists(path_dict['output']['intervention']):
    # collect parallelized output
    c_op.collect_output(os.path.join(path_dict['output']['intervention']))
    
    # write all final run files
    abc_output.write_final_runs(var_to_replace, path_dict)
    
    # paralellize
    c_op.parallelize_input(os.path.join(path_dict['input'], 'Final runs'))
else:
    # write all abc run files
    abc_input.write_abc(var_to_replace, path_dict)
    
    # parallelize
    c_op.parallelize_input(path_dict['output']['intervention'])
    

if False:
    # compare New CEPAC with Old CEPAC
    compare_model = pd.read_excel(os.path.join(path_dict['input'], 'plot_df.xlsx'))
    save_path = os.path.join(path_dict['input'], 'Compare CEPAC old and new')
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    abc_compare.get_lineplots(compare_model, save_path)
    
    # what target is achieved
    def get_target(val):
        
        if val < 50:
            return 'None'
        elif (val >= 50) and (val < 75):
            return '50% reduction in incidence rate'
        else:
            return '75% reduction in incidence rate'
    
    compare_model['Which target is achieved'] = np.zeros(compare_model['Coverage level (%)'].shape)
    for i in compare_model.index:
        compare_model.loc[i, 'Which target is achieved'] = get_target(compare_model.loc[i, 'Percentage reduction in incidence'])
    
    df_pair = compare_model.loc[compare_model['Model type'] == 'New CEPAC', ['Coverage level (%)', 'Coverage time (months)', 'Which target is achieved']]
    plt.figure()
    pp = sns.pairplot(df_pair, hue='Which target is achieved')
    plt.savefig('Pairplot_5years.jpg')

# write final run output to excel
#x = r'C:\Users\Vijeta\Documents\Projects\Brazil PrEP\Transmission runs\CURRENT ANALYSIS\March\SA on dropout (100% uptake in 1 month)\CEPAC in file (SA on dropout percentage)\run this\results'
#link.export_output_to_excel(x, x)



