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
from copy import deepcopy
import abc_input_cov_covtime as abc_input
import abc_output_cov_covtime as abc_output
import abc_final
import cluster_operations as c_op
import link_to_cepac_in_and_out_files as link

#%% Input reading and file creation

if True:
    # path to import in files
    HORIZON = int(60)
    CITY = "Manaus"
    CITY_CODE = CITY[0] + str(10)#str(int(HORIZON/12))
    path_dict = {}
    base = r'/Users/vijetadeshpande/Downloads/MPEC/Brazil/Manaus/2-way SA_10 year'
    path_dict['input'] = os.path.join(base, 'Basefiles')
    path_dict['output'] = {}
    path_dict['output']['intervention'] = os.path.join(base, 'Measurement of community benefit_' + CITY_CODE, "Positive coverage runs_" + CITY_CODE)
    path_dict['output']['status quo'] = os.path.join(base, 'Measurement of community benefit_' + CITY_CODE, "Status quo_" + CITY_CODE)
    path_dict['output']['final runs'] = os.path.join(base, "Final runs_" + CITY_CODE)
    
    # find and replace following variable
    var_to_replace = {'PrEPCoverage': np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6]), 'PrEPDuration': np.array([24, 36, 48, 60])}
    #var_to_replace = {'PrEPCoverage': np.array([0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5, 0.6]), 'PrEPDuration': np.array([24, 36, 48, 60])}
    #{'PrEPCoverage': np.array([0, 0.07, 0.15, 0.22, 0.30]), 'PrEPDuration': np.array([6, 19, 33, 46, 60])} 
    #{'PrEPCoverage': np.array([0.01, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5, 0.6]), 'PrEPDuration': np.array([24, 36, 48, 60])} # 
    
    # check which path exists
    if os.path.exists(path_dict['output']['final runs']):
        # collect parallelized output
        try:
            c_op.collect_output(path_dict['output']['final runs'])
        except:
            pass
        
        # calculate percentage reduction in incidence rate and plot all the results
        final_path = os.path.join(path_dict['output']['final runs'], 'results')
        sq_path = os.path.join(path_dict['output']['status quo'], 'results')
        abc_final.analyze_final_output(final_path, sq_path, HORIZON)
        
        # write excel file for the CEPAC output
        link.export_output_to_excel(final_path, final_path)
    
    elif os.path.exists(path_dict['output']['intervention']):
        # collect parallelized output
        try: 
            c_op.collect_output(os.path.join(path_dict['output']['intervention']))
        except:
            pass
        
        # write all final run files
        abc_output.write_final_runs(var_to_replace, path_dict, HORIZON)
        
        # paralellize
        c_op.parallelize_input(path_dict['output']['final runs'])
    else:
        # write all abc run files
        abc_input.write_abc(var_to_replace, path_dict)
        
        # parallelize
        c_op.parallelize_input(path_dict['output']['intervention'])
    

# compare New CEPAC with Old CEPAC


# write final run output to excel
#x = os.path.join(path_dict['input'], r'Final runs', r'results')
#x = r'/Users/vijetadeshpande/Downloads/MPEC/Brazil/Rio/2-way SA_40%/Status quo/results'
#link.export_output_to_excel(x, x)



