# -*- coding: utf-8 -*-
"""
Created on Wed Sep 11 13:10:57 2019

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
from ggplot import ggplot, geom_line, geom_point, aes, facet_wrap, ggtitle, stat_smooth, geom_vline, geom_hline, scale_x_continuous, scale_y_continuous
from mpl_toolkits.mplot3d import Axes3D


#%% PLOT MINIMUM AGE AT WHICH PrEP COVERAGE CROSSES THE THRESHOLD VALUE OF 
# COVERAGE TO OBSERVE HERD IMMUNITY

# important parameters
input_par = {}
input_par['incidence_rate_100py'] = 4.3 #4.3
input_par['efficacy'] = 0.96
input_par['adherence'] = 0.76
input_par['uptake'] = 0.15
input_par['duration'] = 30
input_par['mortality'] = {}
input_par['mortality']['natural'] = 3.02259 * 10**-5 * 1200
input_par['mortality']['disease'] = 3.27027 * 10**-4 * 1200
input_par['weibull'] = {}
input_par['weibull']['shape'] = 2
input_par['sus_to_inf'] = 5

#%% weibull
def get_weibull(t, coverage = input_par['uptake'], duration = input_par['duration'], shape = input_par['weibull']['shape']):
    scale = -1*np.log(1 - coverage)/np.power(duration, shape)
    tp = 1 - np.exp((scale * np.power((t-1), shape, dtype = float)) - (scale * np.power(t, shape, dtype = float)))
    
    cp = 1 - np.exp((-scale*np.power(t, shape)))
    
    return tp, cp

#%% compartmental model
def get_threshold_crossing(x, y, sus_to_inf):
    # horizon
    time_horizon = np.arange(0,120)
    
    # plotting population
    pop_plot = pd.DataFrame(0, index = np.arange(max(time_horizon)), columns = ['susceptible', 'on_prep', 'infected', 'deaths', 'incident_cases', 'total'])
    
    # let
    target_cov_float = x
    cov_time_horizon_float = y
    start_age = np.ones((len(x), len(time_horizon))) # don't delete (IDK why but this line works sometimes :D) 
    #start_age = np.ones((1, 3600))
    
    #%% define compartments
    compartment = {}
    compartment['infected'] = 10000
    compartment['susceptible'] = sus_to_inf * compartment['infected'] #compartment['infected']*sus_to_inf
    compartment['on_prep'] = 0
    out_dict = {}
    out_dict['reprod_rate'] = []
    out_dict['herd_immunity_threshold'] = []
    out_dict['deaths'] = {}
    out_dict['deaths']['hiv'] = []
    out_dict['deaths']['natural'] = []
    out_dict['incident_cases'] = []
    out_dict['incidence'] = [input_par['incidence_rate_100py']]
    out_dict['coverage_prob'] = []
    out_dict['contact_rate'] = [sus_to_inf]
    out_dict['other_tx'] = []
    #%% differential equations and collection of outcomes over the 10 years period
    for t in range(0, max(time_horizon) + 1):
        
        #%% calculate coverage probability (from transition probability defined by Fatma)
        p_cov, _ = get_weibull(t, coverage = target_cov_float, shape = input_par['weibull']['shape'], duration = cov_time_horizon_float)
        #if p_cov > 0:
        #    print('Coverage probability value is greater than 0')
        #elif p_cov > 1:
        #    print('Coverage probability value is greater than 1')
        #    exit
        
        #%% probability of infection
        inci_t = out_dict['incidence'][t]
        sq_inf = 1 - np.exp(-1*inci_t/1200) 
        int_inf = sq_inf*(1 - input_par['efficacy']*input_par['adherence'])
        
        #%% Account for deats before start of the month
        deaths = (compartment['susceptible'] * input_par['mortality']['natural'] + 
                  compartment['on_prep'] * input_par['mortality']['natural'] + 
                  compartment['infected'] * input_par['mortality']['disease'])/1200 
        compartment['susceptible'] -= compartment['susceptible'] * input_par['mortality']['natural']/1200
        compartment['on_prep'] -= compartment['on_prep'] * input_par['mortality']['natural']/1200
        compartment['infected'] -= compartment['infected'] * input_par['mortality']['disease']/1200
        # track infected and susceptible population at the start of the month
        inf_previous = compartment['infected']
        sus_previous = compartment['susceptible']
        
        # append output
        out_dict['deaths']['hiv'].append(compartment['infected'] * input_par['mortality']['disease']/1200)
        out_dict['deaths']['natural'].append((compartment['susceptible'] * input_par['mortality']['natural'] + compartment['on_prep'] * input_par['mortality']['natural'])/1200)
        
        # check sum
        #%% update population in all compartments
        if t > 0:
            # transfer from on_prep
            compartment['infected'] += compartment['on_prep'] * (-np.log(1 - int_inf))
            compartment['on_prep'] -= compartment['on_prep'] * (-np.log(1 - int_inf))
            
            # transfer from susceptible 
            compartment['on_prep'] += compartment['susceptible'] * -np.log(1 - p_cov)
            compartment['infected'] += compartment['susceptible'] * inci_t/1200
            compartment['susceptible'] -= compartment['susceptible'] * (-np.log(1 - p_cov) + inci_t/1200)
            
        else:
            # only perform outflow from susceptible
            compartment['on_prep'] += compartment['susceptible'] * -np.log(1 - p_cov)
            compartment['infected'] += compartment['susceptible'] * inci_t/1200
            compartment['susceptible'] -= compartment['susceptible'] * (-np.log(1 - p_cov) + inci_t/1200)
            
        # incident cases
        incident_cases = compartment['on_prep'] * (-np.log(1 - int_inf)) + compartment['susceptible'] * (-np.log(1 - sq_inf))
        
        #%% calculate transmission rate or basic reproduction rate
        tx_rate = 1200 * incident_cases/inf_previous # per 100PY
        #tx_rate2 = 1200 * (incident_cases/sus_previous) * (compartment['susceptible']/compartment['infected'])
        #tx_rate3 = 1200 * (incident_cases/sus_previous) * (sus_to_inf) # this uses constant contact rate between sus and inf, therefore not correct method
        #net_reprod_rate = tx_rate * ((susceptible + (on_prep * (1 - efficacy*adherence))) / (susceptible + infected + on_prep))
        #tx_rate4 = out_dict['incidence'][t] * compartment['susceptible']/compartment['infected']
        #%% collect neccessary outcomes
        # basic reprod rate
        out_dict['reprod_rate'].append(tx_rate)
        #out_dict['other_tx'].append(other_tx)
        # coverage threshold for driving basic reproduction rate below 1
        herd_immunity_threshold = np.ones(tx_rate.shape) - (np.ones(tx_rate.shape)/tx_rate)
        out_dict['herd_immunity_threshold'].append(herd_immunity_threshold)
        out_dict['incidence'].append(1200 * incident_cases/sus_previous)
        out_dict['incident_cases'].append(incident_cases)
        out_dict['coverage_prob'].append(p_cov)
        out_dict['contact_rate'].append(compartment['susceptible']/compartment['infected'])
        
        # whether the current age crosses the threshold or not
        age = t * (compartment['on_prep'] * input_par['efficacy'] * input_par['adherence'] / (compartment['on_prep'] + compartment['susceptible'] + compartment['infected']) >  herd_immunity_threshold)
        age = (max(time_horizon) + 2)*(age == 0) + age
        start_age[:, t] = age
        
        # births
        #out_dict['deaths'].append(deaths)
        compartment['susceptible'] += 1 * deaths
        
        # update plotting pop
        if len(x) == 1:       
            for state in pop_plot.columns:
                if state == 'deaths':
                    pop_plot.loc[t, 'deaths'] = deaths
                elif state == 'incident_cases':
                    pop_plot.loc[t, 'incident_cases'] = incident_cases
                elif state == 'total':
                    pop_plot.loc[t, 'total'] = compartment['susceptible'] + compartment['on_prep'] + compartment['infected']
                else:
                    pop_plot.loc[t, state] = compartment[state]
                
        # update incidence
        #input_par['incidence_rate_100py'] = 1200 * incident_cases/sus_previous
        
        
    out_dict['min_age'] = np.amin(start_age, axis = 1)
    
    return out_dict, pop_plot

# plot for uptake probabilities
t_max = 361
time = np.arange(1,t_max)
plot_coverage = pd.DataFrame(0, index = np.arange(1, t_max*2 - 2), columns = ['Transition Probability', 'Cumulative Probability', 'Model'])
plot_coverage = plot_coverage.reset_index()
plot_coverage['Simulation month'] = plot_coverage['index']
for t_float in time:
    plot_coverage.loc[t_float-1, 'Transition Probability'], plot_coverage.loc[t_float, 'Cumulative Probability'] = get_weibull(t = t_float, coverage = input_par['uptake'], duration = input_par['duration'])
    plot_coverage.loc[t_float-1, 'Model'] = 'Quasi-dynamic'
    if True:
        plot_coverage.loc[t_float-1 + t_max-1, 'Transition Probability'], plot_coverage.loc[t_float-1 + t_max-1, 'Cumulative Probability'] = 0.15, 0.15 #get_weibull(t = t_float, coverage = input_par['uptake'], duration = 1)
        plot_coverage.loc[t_float-1 + t_max-1, 'Model'] = 'Static'
        plot_coverage.loc[t_float-1 + t_max-1, 'Simulation month'] = t_float

#plot
save_dir = os.path.dirname(os.path.abspath(__file__))
gg_trans_p = ggplot(aes(x = 'Simulation month', y = 'Transition Probability', color = 'Model'), data = plot_coverage) + geom_line() + ggtitle('Weibull transition probabilities for PrEP uptake \n(Shape = 2, Coverage/Uptake = 15%, Target horizon for coverage/uptake = 30 months)')#\
#geom_vline(aes(xintercept = input_par['duration']), linetype = 'dashed', color = 'gray') + scale_x_continuous(breaks = sort([min(plot_coverage['Simulation month']), max(plot_coverage['Simulation month'])], length.out=5), input_par['duration']) +\
#geom_hline(aes(yintercept = input_par['uptake']), linetype = 'dashed', color = 'gray') + scale_y_continuous(breaks = sort(c(seq(min(plot_coverage['Transition Probability']), max(plot_coverage['Transition Probability']), length.out=5), input_par['uptake']))) +\

gg_cumul_p = ggplot(aes(x = 'index', y = 'Cumulative Probability', color = 'Model'), data = plot_coverage) + geom_line()
gg_trans_p.save(filename = 'Weibull transition probabilities for PrEP uptake')
gg_cumul_p.save(filename = 'Weibull cumulative probabilities for PrEP uptake')
#%% get variation of tx rate
x_target_cov = np.array([0.1])
y_target_time = np.array([30])

res_dict, pop = get_threshold_crossing(x_target_cov, y_target_time, input_par['sus_to_inf'])
check = pop.loc[:, ['susceptible','on_prep','infected']].sum(axis = 1)
pop = pop.reset_index()
plots = {}
for i in ['susceptible','on_prep','infected', 'total']:
    plots[i] = ggplot(aes(x = 'index', y = i), data = pop) + geom_line()
    plots[i].save(i)
     
#%% surface/contour plots

# variables for plotting
sus_to_inf = np.array([1, 6, 15, 22])
target_cov = np.linspace(0.01, 1, 200)
cov_time_horizon = np.linspace(6, 60, 200)

# adjustments
X, Y = np.meshgrid(target_cov, cov_time_horizon)
target_cov_in = np.ravel(X)
cov_time_horizon_in = np.ravel(Y)
threshold_crossings = np.ones((target_cov_in.shape[0], sus_to_inf.shape[0]))


# plotting
idx = -1
for ratio in sus_to_inf:    
    idx += 1
    out_dict_float, _ = get_threshold_crossing(target_cov_in, cov_time_horizon_in, sus_to_inf[idx])
    threshold_crossings[:, idx] = out_dict_float['min_age']

for i in range(len(sus_to_inf)):
    
    # plot
    fig = plt.figure()
    #ax = fig.add_subplot(111, projection='3d')
    x = target_cov
    y = cov_time_horizon
    X, Y = np.meshgrid(x, y)
    zs = threshold_crossings[:,i]
    Z = zs.reshape(X.shape)
    
    
    # ax.plot_surface(X, Y, Z)
    # ax.contour3D(X, Y, Z, 50, cmap='binary')
    # ax.plot_surface(X, Y, Z, rstride=1, cstride=1, cmap='viridis', edgecolor='none')
    # ax.plot_wireframe(X, Y, Z, color='black')
    # ax.contour(X, Y, Z)
    fig, ax = plt.subplots()
    cntr_plt = ax.contour(X, Y, Z)
    
    ax.set_xlabel('Target coverage')
    ax.set_ylabel('Target coverage time horizon')
    ax.clabel(cntr_plt, inline=1, fontsize=10)
    #ax.set_zlabel('Minimum age at which coverage threshold is crossed')
    
    name = 'Herd immunity start age at suscetible to infected ratio = ' + str(sus_to_inf[i])
    plt.savefig(name, bbox_inches='tight')


