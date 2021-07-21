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
import matplotlib as m
from copy import deepcopy

def draw_heatmap_n(data):
    
    #
    data = data.loc[data.loc[:, 'Outcome'] == 'Infections averted (%)', :]
    
    #
    city_data = {}
    idx = -1
    for city in ['Rio', 'Salvador', 'Manaus']:
        idx += 1
        df = deepcopy(data.loc[data.loc[:, 'City'] == city, :])
        df = df.pivot(index = 'Time to max. uptake (months)', 
                      columns = 'PrEP uptake (%)', 
                      values = 'z')
        city_data[idx] = df
    
    fig, axn = plt.subplots(3, 1, sharex=True, sharey=True)
    cbar_ax = fig.add_axes([500, 2000, 3500, 5000])
    
    for i, ax in enumerate(axn.flat):
        sns.heatmap(df, ax=ax,
                    cbar=i == 0,
                    vmin=0, vmax=1,
                    cbar_ax=None if i else cbar_ax)
    
    fig.tight_layout(rect=[0, 0, .9, 1])
    plt.savefig('sample.png')
    
    return

def draw_heatmap(*args, **kwargs):
    #plt.figure(figsize=(10, 5))
    sns.set(font_scale=1.45)
    data = kwargs.pop('data')
    
    #
    try:
        if data['Outcome'].unique()[0] == 'Infections averted (No.)':
            data['z'] = data['z'].astype('int32')
    except:
        pass
    
    #
    d = data.pivot(index=args[1], columns=args[0], values=args[2])
    if data.loc[:, 'Outcome'].values[0] == 'Infections averted (No.)':
        cmap_ = 'PuBu'  #'RdYlGn'#'PuBu'
        fmt_ = 'd'
        center_ = 800
        vmin_ = 300
    else:
        cmap_ = 'Greens'  #'RdYlGn'#'PuBu'
        fmt_ = '0.1f'
        center_ = 23
        vmin_ = 5
    
    
    # if city == manaus then dra colorbar
    if data.loc[:, 'City'].values[0] == 'Rio':
        cbar_ = True
        cbar_kws_ = {'label': data.loc[:, 'Outcome'].values[0], 'use_gridspec': False, 'location': "top", 'pad': 1, "shrink": 0.75}
    else:
        cbar_ = False
        cbar_kws_ = {}
    
    #
    try:
        hmap = sns.heatmap(d, **kwargs, 
                           annot = True, 
                           fmt = fmt_, 
                           cmap = cmap_, 
                           cbar = cbar_,
                           cbar_kws = cbar_kws_,
                           center = center_, vmin = vmin_)
    except:
        print('fail')
        
    
    """
    try:
        hmap = sns.heatmap(d, **kwargs, 
                           annot = True, 
                           fmt = format_, 
                           cmap = colmap, 
                           cbar = colbar,
                           cbar_kws = colbar_kws,
                           center = 800, vmin = 300) # center=2660, vmin=403
    except:
        hmap = sns.heatmap(d, **kwargs, 
                           annot = True, 
                           fmt = '0.1f', 
                           cmap = 'Greens', 
                           cbar = colbar,
                           cbar_kws = colbar_kws,
                           center=23, vmin=5) # center=23, vmin=5
    """
    
        
    hmap.figure.axes[0].invert_yaxis()
    hmap.set_xlabel(X,fontsize=20)
    hmap.set_ylabel(Y,fontsize=20)
    
    return

def save_heatmap(*args, **kwargs):
    
    #
    plt.figure(figsize=(10, 5))
    sns.set(font_scale=1.4)
    data_ = args[0]
    data = data_.loc[data_.loc[:, 'City'] == kwargs['city'], :]
    
    
    #
    try:
        if data['Outcome'].unique()[0] == 'Infections averted (No.)':
            data['z'] = data['z'].astype('int32')
    except:
        pass
    
    #
    d = data.pivot(index = kwargs['x'], columns = kwargs['y'], values = kwargs['z'])
    colmap = 'RdYlGn' #'RdYlGn'#'PuBu'
    
    #
    try:
        hmap = sns.heatmap(d, cbar = False, annot = True, fmt = 'd', cmap = colmap, center = 500, vmin = 200) # center=2660, vmin=403
    except:
        hmap = sns.heatmap(d, cbar = False, annot = True, fmt = '0.1f', cmap = 'Greens')#, center=23, vmin=5) # center=23, vmin=5
    hmap.figure.axes[0].invert_yaxis()
    hmap.set_xlabel(kwargs['y'],fontsize=20)
    hmap.set_ylabel(kwargs['x'],fontsize=20)
    
    #
    filename = kwargs['city'] + '_heatmap_' + kwargs['horizon'] + '.png'
    plot_title = 'City = ' + kwargs['city'] + ' | ' + 'Outcome = ' + 'Infections averted (No.)'
    plt.title(plot_title)
    if kwargs['city'] == 'Manaus':
        plt.xlabel(kwargs['y'])
    else:
        plt.xlabel('')
    plt.savefig(os.path.join(kwargs['basepath'], filename))
    
    
    return


def get_xy_labels(df, x, y):
    
    all_labels = {'x': {}, 'y': {}}
    
    for city in ['Rio', 'Salvador', 'Manaus']:
        df_float = df.loc[df.loc[:, 'City'] == city, :]
        x_unique, y_unique = df_float.loc[:, x].unique(), df_float.loc[:, y].unique()
        x_unique, y_unique = np.array(x_unique).astype(str), np.array(y_unique).astype(str)
        
        all_labels['x'][city] = x_unique
        all_labels['y'][city] = y_unique
        
    
    return all_labels



# expand all data
base = r'/Users/vijetadeshpande/Downloads/MPEC/Brazil/Results/January 2021'#r'/Users/vijetadeshpande/Downloads/MPEC/Brazil/Results/July/July 13, 2020/'
filename = r'OWSA_all outcomes for all cities_60.xlsx'
X, Y = 'PrEP uptake (%)', 'Time to max. uptake (months)' #'PrEP adherence (%)', 'PrEP dropout (%)' 'PrEP uptake (%)', 'Time to max. uptake (months)'
Z = 'Infections averted (No.)'

#
all_data = pd.read_excel(os.path.join(base, filename)).iloc[:, 1:]
col_names = all_data.columns.values
if 'OWSA' in filename:
    col_names[4] = Z
else:
    col_names[2] = Z
all_data.columns = col_names
all_data = all_data.sort_values(by = [X, Y])
all_data[X] = (1 * all_data[X].values).astype(int)
all_data[Y] = (1 * all_data[Y].values).astype(int)
all_data_expand = pd.DataFrame(0, index = np.arange(len(all_data.index) * 2),
                               columns = [X, Y, 'z', 'Outcome', 'City'])
for row in all_data.index:
    idx = row*2
    all_data_expand.loc[idx:idx+1, [X, Y, 'City']] = all_data.loc[row, [X, Y, 'City']].values
    all_data_expand.loc[idx, ['z', 'Outcome']] = [int(all_data.loc[row, 'Infections averted (No.)']), 'Infections averted (No.)']
    all_data_expand.loc[idx+1, ['z', 'Outcome']] = [all_data.loc[row, 'Infections averted (%)'], 'Infections averted (%)']

#
plt.figure(figsize=(10, 5))
all_data_expand = all_data_expand.loc[all_data_expand.loc[:, 'Outcome'] != 0, :]
all_data_expand.loc[:, [X, Y]] = all_data_expand.loc[:, [X, Y]].round(1)

# try this
draw_heatmap_n(all_data_expand)

fg = sns.FacetGrid(all_data_expand, row='City', col = 'Outcome', height = 7)#, aspect = 1.2)
fg.map_dataframe(draw_heatmap, X, Y, 'z', square = True)
                 #cbar = False, square = True)
facecolor=plt.gcf().get_facecolor()

switch = True
for ax in fg.axes.flatten():
    #ax.tick_params(reset = True, axis = 'x', labelbottom = True, labelsize = 20, length = 0, pad = 10)
    #ax.tick_params(axis = 'y', labelsize = 16, length = 0, pad = 10, labelrotation = 90)
    ax.tick_params(reset = True, labelleft = switch, labelbottom = True, labelsize = 16, length = 0, pad = 10)
    switch = not switch
    



"""
all_labels = get_xy_labels(all_data_expand, X, Y)
ax_idx = -1
for ax in fg.axes.flatten():
    ax_idx += 1
    
    if ax_idx == 0:
        x_labels = all_labels['x']['Rio']
        y_labels = all_labels['y']['Rio']
    elif ax_idx == 1:
        x_labels = all_labels['x']['Salvador']
        y_labels = all_labels['y']['Rio']
    elif ax_idx == 2:
        x_labels = all_labels['x']['Manaus']
        y_labels = all_labels['y']['Rio']
        
    #ax.tick_params(axis = 'both', reset = True, which = 'major', labelsize = 16) #(labelbottom=True, labelsize = 16)
    ax.tick_params(labelbottom = True, labelsize = 16)
    ax.set_xticklabels(x_labels)
    ax.set_yticklabels(y_labels)
    
    
# get figure background color

#for ax in fg.axes.flat:
    # set aspect of all axis
    #ax.set_aspect('equal','box')
    # set background color of axis instance
    #ax.set_axis_bgcolor(facecolor)
    

# separate plots
for city in ['Rio', 'Salvador', 'Manaus']:
    save_heatmap(all_data_expand, 
                 x = X, y = Y, z = 'z', 
                 city = city, basepath = base, horizon = '60')
"""


#
savepath = os.path.join(base, 'Basecase_averted infections_all cities_60.png')
plt.savefig(savepath)

# separate plots
for city in ['Rio', 'Salvador', 'Manaus']:
    save_heatmap(all_data_expand, 
                 x = X, y = Y, z = 'z', 
                 city = city, basepath = base, horizon = '60')


    