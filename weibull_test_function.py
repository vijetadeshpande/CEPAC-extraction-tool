# -*- coding: utf-8 -*-
"""
Created on Wed Oct  9 16:10:40 2019

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
from ggplot import ggplot, geom_line, geom_point, aes, facet_wrap, ggtitle, stat_smooth, geom_vline#, ggsave
from mpl_toolkits.mplot3d import Axes3D

# important parameters
input_par = {}
input_par['incidence_rate_100py'] = 4.3 #4.3
input_par['efficacy'] = 1
input_par['adherence'] = 1
input_par['uptake'] = 0.6
input_par['duration'] = 48
input_par['weibull'] = {}
input_par['weibull']['shape'] = 0.5
input_par['sus_to_inf'] = 5

#%% weibull
def get_weibull(t, coverage = input_par['uptake'], duration = input_par['duration'], shape = input_par['weibull']['shape']):
    scale = -1*np.log(1 - coverage)/np.power(duration, shape)
    tp = 1 - np.exp((scale * np.power((t-1), shape, dtype = float)) - (scale * np.power(t, shape, dtype = float)))
    
    scale1 = duration/(np.power((-np.log(1 - coverage)), (1/shape)))
    cdf_p = 1 - np.exp(-np.power(((t-1)/scale1), shape))
    cdf_c = 1 - np.exp(-np.power((t/scale1), shape))
    tp1 = (cdf_c - cdf_p)/(1- cdf_p)
    
    
    return tp, tp1

# plot for uptake probabilities
time = np.arange(1,121)
shape = [1, 1.5, 5] #np.linspace(1, 5, 10)
collect_prob = pd.DataFrame(0, index = time, columns = ['Empty']) #, columns = ['FS 1', 'FS 1.5', 'FS 5', 'PK 1', 'PK 1.5', 'PK 5'])
plot_num = 1
plots = {}
for s in shape:
    plot_prob = pd.DataFrame(0, index = time, columns = ['time', 'Monthly transition probability', 'Formula'])
    row_idx = 1
    for t_float in time:
        tp_FS, tp_PK = get_weibull(t = t_float, coverage = input_par['uptake'], duration = input_par['duration'], shape = s)
        plot_prob.loc[row_idx, 'Monthly transition probability'] = tp_FS
        plot_prob.loc[row_idx + 1, 'Monthly transition probability'] = tp_PK
        plot_prob.loc[row_idx, 'time'] = t_float
        plot_prob.loc[row_idx + 1, 'time'] = t_float
        plot_prob.loc[row_idx, 'Formula'] = 'FS'
        plot_prob.loc[row_idx + 1, 'Formula'] = 'PK'
        
        row_idx += 2
    
    # collect
    collect_prob['FS ' + str(s)] = plot_prob.loc[plot_prob.loc[:, 'Formula'] == 'FS', 'Monthly transition probability'].values
    collect_prob['PK ' + str(s)] = plot_prob.loc[plot_prob.loc[:, 'Formula'] == 'PK', 'Monthly transition probability'].values
    
    # plot
    x = ggplot(aes(x = 'time', y = 'Monthly transition probability', color = 'Formula'), data = plot_prob) + geom_line()
    #name = r'Shape: ' + str(s)# + r', Coverage/Uptake = ' + str(input_par['uptake']*100) + r', Coverage time = ' + str(input_par['duration']) + '.jpg'
    x.save('Weibull' + str(plot_num))
    
    plot_num += 1
