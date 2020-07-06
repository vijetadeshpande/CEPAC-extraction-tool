#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  6 11:55:15 2020

@author: vijetadeshpande
"""

import seaborn as sns
import numpy as np
import pandas as pd
import matplotlib.pylab as plt
import os

def draw_heatmap(*args, **kwargs):
    #plt.figure(figsize=(10, 5))
    sns.set(font_scale=1.2)
    data = kwargs.pop('data')
    
    #
    try:
        if data['Outcome'][0] == 'Infections averted':
            data['z'] = data['z'].astype('int32')
    except:
        pass
    
    #
    d = data.pivot(index=args[1], columns=args[0], values=args[2])
    
    #
    try:
        hmap = sns.heatmap(d, **kwargs, annot = True, cmap = 'PuBu_r', fmt = 'd')
    except:
        hmap = sns.heatmap(d, **kwargs, annot = True, cmap = 'PuBu_r', fmt = '0.1f')
    hmap.figure.axes[0].invert_yaxis()

#fg = sns.FacetGrid(all_data, row='City', size = 7)#, aspect = 1.2)
#fg.map_dataframe(draw_heatmap, 'PrEP uptake (%)', 'Time to max. uptake (months)', 'Infections averted', cbar=False, square = True)
# get figure background color
#facecolor=plt.gcf().get_facecolor()
#for ax in fg.axes.flat:
    # set aspect of all axis
    #ax.set_aspect('equal','box')
    # set background color of axis instance
    #ax.set_axis_bgcolor(facecolor)

#
#base = r'/Users/vijetadeshpande/Downloads/MPEC/Brazil/Manuscript/July 2, 2020'
#savepath = os.path.join(base, 'Averted infections_all cities.png')
#plt.savefig(savepath)
#
#plt.show()

# expand all data
all_data_expand = pd.DataFrame(0, index = np.arange(len(all_data.index) * 2),
                               columns = ['PrEP uptake (%)', 'Time to max. uptake (months)', 'z', 'Outcome', 'City'])
for row in all_data.index:
    idx = row*2
    all_data_expand.loc[idx:idx+1, ['PrEP uptake (%)', 'Time to max. uptake (months)', 'City']] = all_data.loc[row, ['PrEP uptake (%)', 'Time to max. uptake (months)', 'City']].values
    all_data_expand.loc[idx, ['z', 'Outcome']] = [int(all_data.loc[row, 'Infections averted']), 'Infections averted']
    all_data_expand.loc[idx+1, ['z', 'Outcome']] = [all_data.loc[row, 'Infections averted (%)'], 'Infections averted (%)']


fg = sns.FacetGrid(all_data_expand, row='City', col = 'Outcome', size = 7)#, aspect = 1.2)
fg.map_dataframe(draw_heatmap, 'PrEP uptake (%)', 'Time to max. uptake (months)', 'z', cbar=False, square = True)
# get figure background color
facecolor=plt.gcf().get_facecolor()
#for ax in fg.axes.flat:
    # set aspect of all axis
    #ax.set_aspect('equal','box')
    # set background color of axis instance
    #ax.set_axis_bgcolor(facecolor)

#
base = r'/Users/vijetadeshpande/Downloads/MPEC/Brazil/Manuscript/July 2, 2020'
savepath = os.path.join(base, 'Averted infections_all cities1.png')
plt.savefig(savepath)