# -*- coding: utf-8 -*-
"""
Created on Wed Sep  4 16:53:34 2019

@author: Vijeta
"""
import scipy as sp
import link_to_cepac_in_and_out_files as link
from copy import deepcopy
import os
import numpy as np
import matplotlib.pyplot as plt
import math
import timeit
'''
in this file we are preparing training and testing set for NN. NN will 
approximate the performace of CEPAC and eventually be used in optimizing the 
decision of PrEP uptake, PrEP duration and PrEP Shape..

A. Probable decision variables
    1. PrEP Coverage
    2. PrEP Coverage time
    3. PrEP Shape Parameter
B. Variables that might change according to the city and we will change in CEPAC
    1. Incidence (HIVTest tab)
    2. Incidence reduction due to community benefit (HIVTest tab)
    3. Transmission rate multiplier (risk factor multiplier in cohort tab)
    4. HIV infected population (used in DTM)
    5. HIV susceptible population (used in DTM)
C. Variables that might change according to the city but we'lln't change in CEPAC
    1. Initial age (cohort characteristics)
    2. Initial CD4 dist (cohort characteristics)
    3. Acute CD4 dist (HIVTest tab)
    4. Distribution over CD4 strata (cohort characteristics)
    5. Distribution over VL (cohort characteristics)
    6. Acute VL distribution (HIVTest tab)
    7. Index year distribution over VL (used in DTM)
    
At this very initial stage it seems that we need to have 3+5=8 input nodes/vars 
to the NN (or any other regression model)

Therefore, in creating train and test set we need to change the 3+5 variables 
in CEPAC and create corresponding in files. Let's first go for 1000 files, i.e.
approximately 120 variations per variable. 

Let's begin!
'''
#%%
# start timer
start = timeit.default_timer()
 

sample_mod = 10000
sample = {}

# sampling HIV infected population
hiv_inf = [700, 25000]
sample_float = sp.random.uniform(hiv_inf[0], hiv_inf[1], size = sample_mod)
sample['DynamicTransmissionNumHIVPosHRG'] = sample_float

# sampling HIV susceptible population
hiv_sus = [9000, 110000]
sample_float = sp.random.uniform(hiv_sus[0], hiv_sus[1], size = sample_mod)
sample['DynamicTransmissionNumHIVNegHRG'] = sample_float

# sampling incidence from uniform for Incidence
inci_rate_year = [0.3, 7]
inci_prob_month = [0, 0]
for i in range(len(inci_rate_year)):
    inci_prob_month[i] = 1 - (1 - (1 - sp.exp(-inci_rate_year[i])))**(1/12)
sample_inci = np.ones((sample_mod, 3))
sample_inci[:, 0:2] = sp.random.uniform(inci_rate_year[0], inci_rate_year[1], size = (sample_mod, 2))[:]
sample_prob = 1 - np.exp(-1*sample_inci/1200)
sample_float = np.zeros((sample_mod, 8))
for i in range(sample_float.shape[1]):
    if i <= 2:
        sample_float[:, i] = sample_prob[:, 0]
    elif i <= 3:
        sample_float[:, i] = sample_prob[:, 1]
    else:
        sample_float[:, i] = sample_prob[:, 2]
sample['HIVmthIncidMale'] = sample_float
del sample_prob

# sampling transmission rate multiplier
# transmission rate mutiplier is a dependent parameter f(inci, infected at start susceptible at start)
# trans_mul = [1, 25]
contact_rate = sample['DynamicTransmissionNumHIVNegHRG']/sample['DynamicTransmissionNumHIVPosHRG']
# mutiplier need weighted average of generic rates for calculation (assume that does not change)
weighted_average_generic_tx_rate = 4.84
sample['TransmissionRiskMultiplier_T3'] = np.zeros((sample_mod, 3))
for i in range(sample['TransmissionRiskMultiplier_T3'].shape[1]):
    sample['TransmissionRiskMultiplier_T3'][:, i] = np.multiply(sample_inci[:, i], contact_rate)/weighted_average_generic_tx_rate

# sampling incidence reduction
inci_red = [0, 40]
sample_float = sp.random.uniform(inci_red[0], inci_red[1], size = sample_mod)
sample['incidence reduction'] = sample_float/100

# sampling PrEP coverage
prep_cov = [0.01, 0.4]
sample_float = sp.random.uniform(prep_cov[0], prep_cov[1], size = sample_mod)
sample['PrEPCoverage'] = sample_float

# sampling PrEP coverage time
prep_cov_t = [6, 60]
sample_float = sp.random.uniform(prep_cov_t[0], prep_cov_t[1], size = sample_mod)
sample['PrEPDuration'] = sample_float

# sampling PrEP coverage shape
prep_cov_s = [0.1, 5]
sample_float = sp.random.uniform(prep_cov_s[0], prep_cov_s[1], size = sample_mod)/10
sample['PrEPShape'] = sample_float

# we'll replace values in cepac input sheet one by one
path = {"Input": r"C:\Users\Vijeta\Documents\Projects\Brazil PrEP\NN\RNN experiment"}
cepac_in_dict = link.import_all_cepac_in_files(path["Input"])

# list of variables to replace in cepac in file
var_list = ['PrEPCoverage', 'PrEPDuration', 'PrEPShape', 'HIVIncidReductionCoefficient', 'HIVmthIncidMale', 'DynamicTransmissionNumHIVPosHRG', 'DynamicTransmissionNumHIVNegHRG', 'TransmissionRiskMultiplier_T3']

# required vars
efficacy = 0.65
adherence = 0.739
stop_time = 60


# aux function
def find_and_replace(df_in, var, val = []):
    #
    df_out = deepcopy(df_in)
    idx = df_out.loc[df_out.loc[:,0] == var, :].index.values[0]
    start_col = 1
    if var in ['HIVmthIncidMale', 'PrepIncidMale']:
        start_col += 1
    col = df_out.iloc[idx, :].dropna().index[start_col:].values
    if var == "TransmissionRiskMultiplier_T3":
        idx = [idx-2, idx - 1, idx]
        col = max(col)
    
    
    if val == []:
        return df_out, idx, col
    else:
        df_out.iloc[idx, col] = val
        return df_out

for file in cepac_in_dict:
    for row in range(0,sample_mod):
        float_df = deepcopy(cepac_in_dict[file])
        for var in var_list:
            if var == 'HIVIncidReductionCoefficient':       
                # replacing reduction coefficient
                red_coeff = -1*stop_time/sp.log(1 - sample['incidence reduction'][row])
                float_df = find_and_replace(float_df, var, red_coeff)
                
            elif var == 'HIVmthIncidMale':
                # replacing incidence value
                float_df = find_and_replace(float_df, var, sample[var][row])
                prep_incid = sample[var][row] * (1 - efficacy*adherence) 
                float_df = find_and_replace(float_df, 'PrepIncidMale', prep_incid)
            
            else:
                float_df = find_and_replace(float_df, var, sample[var][row])
                
        
        # write file
        if row%10 == 0:
            name_extension = "CEPAC input set %d"%(row/10)
        run_path = os.path.join(path["Input"], name_extension)
        if not os.path.exists(run_path):
            os.makedirs(run_path)
        name = 'cepac_run' + str(row) + r'.in' 
        link.write_cepac_in_file(os.path.join(run_path, name), float_df)


# stop timer
stop = timeit.default_timer()

print('Time: ', stop - start) 

#%%
#def weib(t, shape):
#    coverage = 0.01
#    duration = 120
#    scale = -np.log(1 - coverage)/(duration**shape)
#    tp = 1 - np.exp(scale*(math.pow(t, shape) - math.pow(t+1, shape)))

#    return tp
        
#time = np.arange(0,120)
#shape = 1.1
#p = []
#for t in time:
#    p.append(weib(t, shape))

#plt.plot(p)


#sample_df = pd.DataFrame()
#for var in sample:
    #sample_df[var] = sample[var]

#sample_df.to_csv(r'C:\Users\Vijeta\Documents\Projects\Brazil PrEP\NN\inputs.csv', index = False)
