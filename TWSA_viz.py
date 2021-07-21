#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 30 12:57:29 2020

@author: vijetadeshpande
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sb
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

#
def monthly_prob(prob_y):
    rate_y = -1 * np.log(1 - prob_y)
    rate_m = rate_y/12
    prob_m = 1 - np.exp(-1 * rate_m)
    
    return prob_m


# user input
city = 'Manaus'
HORIZON = 120
COHORT = 20000000
TOTAL_VARVAL = 4
base = os.path.join(r'/Users/vijetadeshpande/Downloads/MPEC/Brazil', city, r'2-way SA_surf')

#
POP_DICT = {'Rio': 94104, 'Salvador': 41728, 'Manaus': 45937}
SUS_SIZE = POP_DICT[city]
if city == 'Rio':
    min_adh, max_adh = 0.627, 0.692 #0.66
    min_drp, max_drp = 0.1464, 0.1939
elif city == 'Salvador':
    SUS_SIZE
    min_adh, max_adh = 0.590, 0.708 #0.649
    min_drp, max_drp = 0.1370, 0.2267
elif city == 'Manaus':
    SUS_SIZE
    min_adh, max_adh = 0.643, 0.727 #0.685
    min_drp, max_drp = 0.1328, 0.1978


#
val_map = {'PrEPAdherence': [0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.80, 0.85], 'PrEPDroputPostThreshold': monthly_prob(np.array([0, 0.05, 0.1, 0.15, 0.20, 0.25]))}
val_map['PrEPAdherence'] = np.sort(np.concatenate((val_map['PrEPAdherence'], [min_adh, max_adh])))
val_map['PrEPDroputPostThreshold'] = np.sort(np.concatenate((val_map['PrEPDroputPostThreshold'], monthly_prob(np.array([min_drp, max_drp])))))

#
var_list = ['PrEPAdherence', 'PrEPDroputPostThreshold']
var_name = {'PrEPAdherence': 'Adherence (%)',
            'HIVtestFreqInterval': 'Tests (per year)',
            'PrEPDroputPostThreshold': 'Dropout (%)'}

#
def yearly_prob(prob_m):
    rate_m = -1 * np.log(1 - prob_m)
    rate_y = 12 * rate_m
    prob_y = 1 - np.exp(-1 * rate_y)
    
    return prob_y

def extract_percentage_decline_value(df, cov, cov_t, z_var):
    cov_idx = df.index[df.loc[:, 'PrEP uptake (%)'] == np.floor(cov)].values
    cov_t_idx = df.index[df.loc[:, 'Time to max. uptake (months)'] == np.floor(cov_t)].values
    idx = set(cov_idx).intersection(set(cov_t_idx)).pop()

    return df.loc[idx, z_var]

def save_heatmaps(plot_dict, save_path, z_var):
    
    #
    x_var = 'PrEP adherence (%)'
    y_var = 'PrEP dropout (%)'
    
    
    # heat plot for final runs
    df = plot_dict["percentage reduction"]
    # surface plot
    df = df.loc[:, [x_var, y_var, z_var]]
    
    #
    val = {'x': np.sort(df[x_var].unique()), 'y': np.sort(df[y_var].unique())}
    x_grid, y_grid = np.meshgrid(val['x'], val['y'])
    
    #
    x = np.ravel(x_grid)
    y = np.ravel(y_grid)
    z = []
    
    #
    for i in range(len(x)):
        z.append(extract_percentage_decline_value(df, y[i], x[i], z_var))
    
    #
    sb_heatmap = pd.DataFrame()
    sb_heatmap[x_var] = np.floor(x).astype(int)
    sb_heatmap[y_var] = np.floor(y).astype(int)
    sb_heatmap[z_var] = z
    sb_heatmap = sb_heatmap.sort_values(by = y_var)
    heatmap_df = pd.pivot(data = sb_heatmap,
                       index = x_var,
                       columns = y_var,
                       values = z_var)
    
    # choose color theme
    #cmap = cm.get_cmap('RdYlGn')
    cmap = 'PuBu_r' #'Reds'
    #cmap = 'coolwarm'
    #cmap = sb.cm._cmap_r
    #my_col_map = ["#eff3ff", "#bdd7e7", "#6baed6", "#3182bd", "#08519c"] # high point is dark blue
    #my_col_map_r = ["#08519c", "#3182bd", "#6baed6", "#bdd7e7", "#eff3ff"] # high point is white
    #cmap = sb.color_palette(my_col_map_r)
    
    #
    plt.figure(figsize=(10, 5))
    sb.set(font_scale=1.2)
    if z_var in ['Percentage reduction in incidence rate', 'Infections averted (%)']:
        fmt_z = '0.1f'
    else:
        fmt_z = 'd'
    
    #    
    heatmap_plot = sb.heatmap(heatmap_df, annot = True, fmt = fmt_z, linewidths = 0.2, cmap = cmap, cbar_kws={'label': z_var})
    heatmap_plot.figure.axes[0].invert_yaxis()
    # if we need to rotate the axis ticks
    heatmap_plot.figure.savefig(os.path.join(save_path, z_var + '.jpg'))
    
    return


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
    sqpath = os.path.join(base, 'Common runs', 'SQ', 'results')
    readbase = os.path.join(basepath, 'Final runs', 'Final runs_var1=PrEPAdherence_var2=PrEPDroputPostThreshold', 'results')
    writebase = os.path.join(base, 'Results')
    
    # collect output
    try:
        c_op.collect_output(os.path.join(readbase, '..'))
    except:
        pass
    
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
        plot_df.loc[idx, 'PrEP adherence (%)'] = 100 * float(file.split('=')[1][0:6])
        plot_df.loc[idx, 'PrEP dropout (%)'] = 100 * yearly_prob(float(file.split('=')[2][0:6]))
        plot_df.loc[idx, 'Averted infections'] = averted_inf
        

# heatplot

# surface plot
plot_df = plot_df.sort_values(by = ['PrEP adherence (%)', 'PrEP dropout (%)'])    
    
# Make the plot
fig = plt.figure(figsize = (14, 10.5), dpi = 120)
ax = fig.gca(projection='3d')
 
# to Add a color bar which maps values to colors.
surf=ax.plot_trisurf(plot_df['PrEP dropout (%)'],
                     plot_df['PrEP adherence (%)'],  
                     plot_df['Averted infections'], 
                     cmap='RdYlGn', 
                     linewidth=0.1,
                     edgecolor = 'black')
fig.colorbar(surf, shrink=0.7, aspect=5)
ax.view_init(30, 60)
ax.set_xlabel('PrEP dropout (%)', fontsize = 'xx-large', labelpad = 20)
ax.set_ylabel('PrEP adherence (%)', fontsize = 'xx-large', labelpad = 20)
ax.set_zlabel('Averted infections', fontsize = 'xx-large', labelpad = 20)
plt.rcParams['xtick.labelsize'] = 20
plt.rcParams['ytick.labelsize'] = 20
plt.rcParams['xtick.major.pad']='0'
plt.rcParams['ytick.major.pad']='0'
#plt.rcParams['ztick.labelsize'] = 20
plt.savefig(os.path.join(writebase, 'Adherence-Dropout surface plot_5 years.png'))
plt.show()

"""
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

"""

        