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
    HORIZON = int(120)
    CITY = "Rio"
    CITY_CODE = CITY[0] + str(10)#str(int(HORIZON/12))
    path_dict = {}
    base = r'/Users/vijetadeshpande/Downloads/MPEC/Brazil/Rio/2-way SA_10 year'#r'/Users/vijetadeshpande/Downloads/MPEC/Brazil/Salvador/2-way SA_10 year'
    path_dict['input'] = os.path.join(base, 'Basefiles')
    path_dict['output'] = {}
    path_dict['output']['intervention'] = os.path.join(base, 'Measurement of community benefit_' + CITY_CODE, "Positive coverage runs_" + CITY_CODE)
    path_dict['output']['status quo'] = os.path.join(base, 'Measurement of community benefit_' + CITY_CODE, "Status quo_" + CITY_CODE)
    path_dict['output']['final runs'] = os.path.join(base, "Final runs_" + CITY_CODE)
    
    # find and replace following variable
    #var_to_replace = {'PrEPCoverage': np.array([1]), 'PrEPDuration': np.array([1])}
    var_to_replace = {'PrEPCoverage': np.array([0.9, 0.95, 1]), 'PrEPDuration': np.array([1, 24, 60])}

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
        abc_final.analyze_final_output(final_path, sq_path, HORIZON, CITY)
        
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
"""
#
new_path = r'/Users/vijetadeshpande/Downloads/MPEC/Brazil/Rio/ART CHECK1/Compare different ART parameter setting1/2-way SA/Measurement of community benefit_R10/Status quo_R10/SQ.in'
old_path = r'/Users/vijetadeshpande/Downloads/MPEC/Brazil/Rio/2-way SA_10 year/Measurement of community benefit_R10/Status quo_R10/SQ.in'
new_sq = link.read_cepac_in_file(new_path)
old_sq = link.read_cepac_in_file(old_path)

#
mismatch_idx, mismatch_idx1 = [], []
mismatch_data, mismatch_data1 = {}, {}
sq = deepcopy(new_sq)
for row in range(0, 1005):
    x = old_sq.iloc[row, :].dropna()
    y = new_sq.iloc[row, :].dropna()
    if (x != y).values.astype(int).sum() > 0:
        mismatch_idx.append(row)
        mismatch_data[row] = pd.DataFrame([x, y])
        if not row in [195, 219, 995, 996]: # [LTGU, PTR, Initial suppression, Late failure]
            sq.iloc[row, 0:len(x)] = x

for row in range(0, 1005):
    x = old_sq.iloc[row, :].dropna()
    y = sq.iloc[row, :].dropna()
    if (x != y).values.astype(int).sum() > 0:
        mismatch_idx1.append(row)
        mismatch_data1[row] = pd.DataFrame([x, y])

#
link.write_cepac_in_file(r'/Users/vijetadeshpande/Downloads/MPEC/Brazil/Rio/ART CHECK1/Compare different ART parameter setting1/2-way SA/Measurement of community benefit_R10/Status quo_R10/NEW_SQ.in', sq)
    

# write final run output to excel
x = r'/Users/vijetadeshpande/Downloads/MPEC/Brazil/Manaus/Goals OWSA/Common runs/SQ'
try:
    c_op.collect_output(x)
except:
    pass
x = os.path.join(x, 'results')
link.export_output_to_excel(x, x, mod = 'treatment')


# parallelize
x = r'/Users/vijetadeshpande/Downloads/MPEC/HPTN/SA on proportion of tx/50cPrEP/LACAB/Final runs_LACAB/Final runs for var = DynamicTransmissionPropHRGAttrib'
c_op.parallelize_input(x)

"""


