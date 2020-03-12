# -*- coding: utf-8 -*-
"""
Created on Tue Sep 24 18:18:17 2019

@author: Vijeta
"""
import scipy as sp
import link_to_cepac_in_and_out_files as link
import pandas as pd
from copy import deepcopy
import os
import numpy as np
import matplotlib.pyplot as plt
import math
from ggplot import ggplot, geom_line, geom_point, aes, facet_wrap, ggtitle, stat_smooth, geom_vline
from mpl_toolkits.mplot3d import Axes3D

# aux function
def get_input_par(age):
    out = {}
    
    return out

def get_weibull_coverage(weibull_dict, age):
    # unroll dictionary
    target_coverage = weibull_dict['target_coverage'][age]
    target_horizon = weibull_dict['target_horizon'][age]
    t = weibull_dict['prep_program_age']
    shape = weibull_dict['shape'][age]
    # calculate scale
    scale = -1*np.log(1 - target_coverage)/np.power(target_horizon, shape)
    # calculate transition probability
    p_coverage = 1 - np.exp((scale * np.power(t, shape, dtype = float)) - (scale * np.power(t+1, shape, dtype = float)))
    
    return p_coverage

def get_vector(length):
    return np.ones((length))

def get_rate_matrix(compartments, par_dict, age, weibull_dict):
    
    if True:
        compartments = deepcopy(compartments)
        par_dict = deepcopy(par_dict)
        weibull_dict = deepcopy(weibull_dict)
    
    # get parameters required for rate matrix
    #par_dict = get_input_par(age)
    # create emty rate matrix
    Q = pd.DataFrame(0, index = compartments, columns = compartments)
    #%% unidentified sus
    Q.loc['unidentified_susceptible', 'identified_susceptible'] = 1 # assumption
    Q.loc['unidentified_susceptible', 'deceased'] = par_dict['mortality']['natural'][age]
    
    #%% identified sus
    p_cov = get_weibull_coverage(weibull_dict, age)
    Q.loc['identified_susceptible', 'on_prep'] = -math.log(1 - p_cov)
    Q.loc['identified_susceptible', 'identified_infected'] = par_dict['natural_incidence'][age]
    Q.loc['identified_susceptible', 'deceased'] = par_dict['mortality']['natural'][age]

    #%% on prep
    Q.loc['on_prep', 'identified_infected'] = par_dict['intervened_incidence'][age]
    Q.loc['on_prep', 'deceased'] = par_dict['mortality']['natural'][age]
    p_fail = 1 - par_dict['adherence'][age]*par_dict['efficacy'][age]
    Q.loc['on_prep', 'identified_susceptible'] = -math.log(1 - p_fail)
    
    #%% unidentified infected
    Q.loc['unidentified_infected', 'identified_infected'] = 1 # assumption
    Q.loc['unidentified_infected', 'deceased'] = par_dict['mortality']['hiv_off_art'][age]
    
    #%% identified infected
    Q.loc['identified_infected', 'infected_on_art'] = 1 # assumtion
    Q.loc['identified_infected', 'infected_off_art'] = 0 # assumption
    Q.loc['identified_infected', 'deceased'] = par_dict['mortality']['hiv_off_art'][age]
    #%% on art
    Q.loc['infected_on_art', 'deceased'] = par_dict['mortality']['hiv_on_art'][age]
    
    #%% off art
    Q.loc['infected_off_art', 'deceased'] = par_dict['mortality']['hiv_off_art'][age]
    
    #%% deceased
    Q.loc['deceased', 'unidentified_susceptible'] = 1 # births == deaths
    
    #%% make diagonal elements = -1 * sum of all other in that row
    for d_element in range(Q.shape[0]):
        Q.iloc[d_element,d_element] = -1*Q.iloc[d_element, :].sum()
    
    return Q

def get_tpm(Q):
    
    if True:
        Q = deepcopy(Q)
        tpm = pd.DataFrame(0, index = Q.index, columns = Q.columns)
    if not isinstance(Q, pd.DataFrame):
        return None
    
    # fill up the deceased column first
    tpm.loc[:, 'deceased'] = np.ones((Q.loc[:, 'deceased'].shape)) - np.exp(-1 * Q.loc[:, 'deceased'].values)
    tpm.loc['deceased', 'deceased'] = 0
    
    # few adjustments
    Q.loc[:, 'deceased'] = 0
    for row in Q.index:
        Q.loc[row, row] = 1
        tpm.loc[row, :'infected_off_art'] = (1 - tpm.loc[row, 'deceased']) * (Q.loc[row, :'infected_off_art'].values/Q.loc[row, :'infected_off_art'].values.sum())
        
    
    return tpm

def get_stationary_dist(tpm):
    
    if True:
        tpm = deepcopy(tpm)
    
    # get the steady state distribution
    tpm_float = np.matrix(tpm)
    pie = pd.DataFrame((np.linalg.matrix_power(tpm_float, 1000))[:][0])
    pie.columns = tpm.columns
    
    return pie

def simulate_differential_eq(pop, Q, age, compartments, births = 0, delta_t = 1):
    if not (isinstance(pop, pd.DataFrame) and isinstance(Q, pd.DataFrame) and isinstance(delta_t, int)):
        return None
    
    # calculate change in population
    delta_pop = pd.DataFrame(0, index = Q.index, columns = Q.columns)
    for state in Q.columns:
        delta_pop.loc[state, :] = pop.loc[state, age] * Q.loc[state, :]
    
    # outlet from age
    pop.loc[:, age] -= -1*np.diag(delta_pop)

    # inlet in age+1
    for state in Q.columns:
        delta_pop.loc[state, state] = 0
    pop.loc[:, age+1] += delta_pop.sum(axis = 0).values #- (pop.loc[state, age] * Q.loc[state, state])
        
    return pop

def expand_incidence(i_in, age_stratas):
    i_out = np.zeros(100)
    idx = -1
    a_p = 0
    for a_c in age_stratas:
        idx += 1
        i_out[a_p:a_c] = i_in[idx]
        a_p = a_c
    # convert to rate/person-month'
    i_out = i_out/1200
    
    return i_out

def get_intervened_incidence(i_in, e, a):
    i_out = i_in * (np.ones((e.shape)) - e*a)
    return i_out

