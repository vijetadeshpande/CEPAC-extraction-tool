# -*- coding: utf-8 -*-
"""
Created on Mon Aug  5 14:43:56 2019

@author: Vijeta
"""
import math
from copy import deepcopy

def calculate_dependent_var_value(df, dep_indep_var_set, val):
    
    df = deepcopy(df)
    
    if dep_indep_var_set['y'] == 'HIVIncidReductionCoefficient':
        
        # reduction coefficient will be as follows
        if (0.01*val['x_user_in']['percentage_reduction']) < 1:
            red_coeff = -1*val['x_cepac']['HIVIncidReductionStopTime']/(math.log(1 - (0.01*val['x_user_in']['percentage_reduction'])))
        else:
            red_coeff = -1*val['x_cepac']['HIVIncidReductionStopTime']/math.log(10**-100)
        
        # replace value
        df.loc[df.loc[:, 0] == 'HIVIncidReductionCoefficient', 1] = red_coeff
        
        # we don't want to use dynamic transmissions module
        df.loc[df.loc[:, 0] == 'UseDynamicTransmission', 1] = 0
        
    elif dep_indep_var_set['y'] in ['PrepIncidMale', 'PrepIncidFemale']:
        
        # calculate HIV incidence on PrEP
        hiv_incidence_on_prep_male = val['x_cepac']['PrepIncidMale'] * (1 - (val['x_user_in']['prep efficacy']*val['x_user_in']['prep adherence']))
        hiv_incidence_on_prep_female = val['x_cepac']['PrepIncidFemale'] * (1 - (val['x_user_in']['prep efficacy']*val['x_user_in']['prep adherence']))
        
        # replace the values
        df.loc[df.loc[:, 0] == 'PrepIncidMale', 2:] = hiv_incidence_on_prep_male
        df.loc[df.loc[:, 0] == 'PrepIncidFemale', 2:] = hiv_incidence_on_prep_female
        
    # UseHIVIncidReduction should be 1
    df.loc[df.loc[:, 0] == 'UseHIVIncidReduction', 1] = 1
    
    return df