#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 30 12:57:29 2020

@author: vijetadeshpande
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import numpy as np
import itertools
import sys
import link_to_cepac_in_and_out_files as link
import cluster_operations as c_op
import TextFileOperations as t_op
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 unused import
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter
import numpy as np


# user input
HORIZON = 60
COHORT = 20000000
SUS_SIZE = 94104 #{'r': 94104, 's': 41728, 'm': 45937}
TOTAL_VARVAL = 4
base = r'/Users/vijetadeshpande/Downloads/MPEC/Brazil/Rio/2-way SA_surf'
val_map = {'PrEPAdherence': [0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.80, 0.86], 
           'PrEPDroputPostThreshold': [0, 0.05, 0.1, 0.15, 0.20, 0.25]}
var_list = ['PrEPAdherence', 'PrEPDroputPostThreshold']
var_name = {'PrEPAdherence': 'Adherence (%)',
            'HIVtestFreqInterval': 'Tests (per year)',
            'PrEPDroputPostThreshold': 'Dropout (%)'}

#
interventions = list(itertools.product(val_map['PrEPAdherence'], val_map['PrEPDroputPostThreshold']))

strategies = ['30 in 36 months']#['30 in 36 months', '30 in 48 months', '40 in 36 months', '40 in 48 months']

# initiate space to save results
plot_df = pd.DataFrame(0, index = np.arange(len(interventions)), 
                       columns = ['PrEP adherence (%)', 'PrEP dropout (%)', 'Averted infections'])

idx = -1
for strategy in strategies:
    print(strategy)

    #
    basepath = os.path.join(base, strategy)
    sqpath = os.path.join(base, 'Common runs', 'results')
    readbase = os.path.join(basepath, 'Final runs', 'Final runs_var1=PrEPAdherence_var2=PrEPDroputPostThreshold', 'results')
    writebase = os.path.join(base, 'Results')
    
    # import all cepac out files
    cepac_outputs = link.import_all_cepac_out_files(readbase, module = 'regression')
    cepac_outputs['status quo'] = link.import_all_cepac_out_files(sqpath, module = 'regression')['SQ']
    
    #
    idx = -1
    for file in cepac_outputs:
        if file == 'status quo':
            continue
        
        #
        idx += 1
        
        # calculate averted infections
        averted_inf = (cepac_outputs['status quo']['infections'] - cepac_outputs[file]['infections'])[0:HORIZON].sum()
        percent_averted_inf = averted_inf / cepac_outputs[file]['infections'][0:HORIZON].sum()
        averted_tx = (cepac_outputs['status quo']['transmissions'] - cepac_outputs[file]['transmissions'])[0:HORIZON].sum()
        percent_averted_tx = averted_tx / cepac_outputs[file]['transmissions'][0:HORIZON].sum()
        
        # adjust values to the population size
        averted_inf = SUS_SIZE * (averted_inf/COHORT)
        averted_tx = SUS_SIZE * (averted_tx/COHORT)
        
        #
        plot_df.loc[idx, 'PrEP adherence (%)'] = float(file.split('=')[1][0:6])
        plot_df.loc[idx, 'PrEP dropout (%)'] = float(file.split('=')[2][0:6])
        plot_df.loc[idx, 'Averted infections'] = averted_inf
        

# surface plot
plot_df = plot_df.sort_values(by = ['PrEP adherence (%)', 'PrEP dropout (%)'])    
    
# Make the plot
fig = plt.figure(figsize = (12, 9), dpi = 120)
ax = fig.gca(projection='3d')
 
# to Add a color bar which maps values to colors.
surf=ax.plot_trisurf(plot_df['PrEP dropout (%)'],
                     plot_df['PrEP adherence (%)'],  
                     plot_df['Averted infections'], 
                     cmap='PuBu_r', 
                     linewidth=0.1,
                     edgecolor = 'black')
fig.colorbar(surf, shrink=0.7, aspect=5)
ax.view_init(30, 30)
plt.savefig(os.path.join(writebase, 'Adherence-Dropout surface plot.png'))
plt.show()

#
fig = plt.figure()
ax = fig.gca(projection='3d')

# Make data.
X = plot_df['PrEP adherence (%)'].unique()
Y = plot_df['PrEP dropout (%)'].unique()
X, Y = np.meshgrid(X, Y)
Z = np.reshape(plot_df['Averted infections'].values, X.shape)

# Plot the surface.
surf = ax.plot_surface(X, Y, Z, cmap='binary',
                       linewidth=0, antialiased=False)

# Customize the z axis.
ax.set_zlim(-1.01, 1.01)
ax.zaxis.set_major_locator(LinearLocator(10))
ax.zaxis.set_major_formatter(FormatStrFormatter('%.02f'))

# Add a color bar which maps values to colors.
fig.colorbar(surf, shrink=0.5, aspect=5)

plt.show()
        