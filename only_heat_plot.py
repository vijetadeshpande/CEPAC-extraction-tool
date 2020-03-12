#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 15 17:27:55 2019

@author: vijetadeshpande
"""

#from processes_on_cepac_input import CepacInput
#from processes_on_cepac_output import CepacOutput
#from processes_on_cepac_output import get_comparative_results
#from ProjectDetails import ProjectDetails
#import dynamic_transmissions_module as dtm
#import os 
import pandas as pd
import numpy as np
#import visualization as viz
#import link_to_cepac_in_and_out_files as link
from copy import deepcopy
#import link_to_cepac_in_and_out_files as link
#import re
#import transmission_algorithm as tx_algo
import matplotlib.pyplot as plt
import seaborn as sb
import matplotlib.cm as cm

#%% Aux functions

# function for creating map
def get_mapped(val, label):
    out_dict = {'value': val, 'label': label}
    return out_dict

# function for plotting
def get_heatplot(data_map, plot_name, ytick_angle = None):
    # creat df to plot
    sb_heatmap = pd.DataFrame()
    for k in data_map:
        sb_heatmap[data_map[k]['label']] = data_map[k]['value']
    sb_heatmap = sb_heatmap.sort_values(by = data_map['z']['label'])
    plot_df = pd.pivot(data = sb_heatmap,
                       index = data_map['y']['label'], 
                       columns = data_map['x']['label'], 
                       values = data_map['z']['label'])
    
    # choose color theme
    #cmap = cm.get_cmap('RdYlGn')
    cmap = 'PuBu' #'Reds'
    #cmap = 'coolwarm'
    #cmap = sb.cm._cmap_r
    my_col_map = ["#eff3ff", "#bdd7e7", "#6baed6", "#3182bd", "#08519c"]
    # ["f7fbff", "deebf7", "c6dbef", "9ecae1", "6baed6", "4292c6", "2171b5", "084594"]
    my_col_map_r = ["#08519c", "#3182bd", "#6baed6", "#bdd7e7", "#eff3ff"]
    cmap = sb.color_palette(my_col_map)
                  
    # create figure
    plt.figure(figsize=(10, 5))
    heatmap_plot = sb.heatmap(plot_df, annot = True, fmt = '0.2f', linewidths = 0.2, cmap=cmap, cbar_kws={'label': data_map['z']['label']})
    heatmap_plot.figure.axes[0].invert_yaxis()
    heatmap_plot.set_yticklabels(heatmap_plot.get_yticklabels(), fontsize = 14)
    heatmap_plot.set_xticklabels(heatmap_plot.get_xticklabels(), fontsize = 14)
    if not ytick_angle == None:
        heatmap_plot.set_yticklabels(heatmap_plot.get_yticklabels(), rotation = ytick_angle)
    sb.set(font_scale=1.2)
    heatmap_plot.figure.savefig(plot_name)
    #fig, ax = plt.subplots()
    #cntr_plt = ax.contour(x_grid, y_grid, z_grid)


#%% mock data
val = {"PrEPDuration": [24, 36, 48, 60], "PrEPCoverage": [1, 5, 10, 15, 20, 25, 30, 40, 50, 60], "City": ["Rio", "Curitiba", "Sao Paulo", "Belem", "Recife", "Salvador"]}
cov_t_grid, cov_grid = np.meshgrid(val['PrEPDuration'], val['PrEPCoverage'])
"""
con_float = np.array([6.97, 5.51, 4.18])
rand_red = deepcopy(con_float)
for i in range(len(val["PrEPCoverage"]) - 1):
    con_float += np.array((i+0.1) * np.ones(len(val["PrEPDuration"])))
    rand_red = np.concatenate([rand_red, con_float])
con_float = [3.03, 3.07, 3.12]
rand_inci = deepcopy(con_float)
for i in range(len(val["PrEPCoverage"]) - 1):
    con_float -= np.multiply(np.true_divide(i+1, 10), np.ones(len(val["PrEPDuration"])))
    rand_inci = np.concatenate([rand_inci, con_float])
"""
# select x, y and z variables
rand_red = [55.41325537, 55, 55, 55, 56.10084284, 55.40994448, 56.34404021, 56.35450211,
            57.17443334,56.98927224,56.70130586,56.07582024, 58.50298488, 57.9504303, 57.05553868, 56.36865902, 58.97816466, 58.39741367, 56.98652891, 57.19360113, 59.39739375, 58.59221488, 58.15762954, 57.02200735, 60.19699808, 58.88760848, 58.54442596, 57.49073615, 62.39686102, 60.22001782, 59.3405657, 57.59111908,
            64.54173497, 61.34700739, 59.76254859, 58.04113206, 69.11392847, 63.49181287, 61.29529184, 59.41737427]

rand_inci = [1.759104256, 1.7,1.7,1.7,1.71644189,1.752413261,1.741705344,1.792221266,1.70156953,1.729392836,1.739763816,1.758263567,1.661549139,1.69794138,1.731957915,1.745208915,1.641562546,1.682874508,1.728072295,1.721293023,1.631233507,1.665460794,1.68009982,1.700557087,1.566588362,1.626666339,1.65997893,1.718433258,1.48029287,1.550887692,1.651442483,1.690107875,1.42288581,1.530340984,1.579439581,1.648906437,1.242259488,1.476257783,1.565063589,1.62500562]   
coverage = np.ravel(cov_grid)
coverage_time = np.ravel(cov_t_grid)
incidence = np.array(rand_inci) 
incidence_reduction = np.array(rand_red)

#%% first heatplot (x = cov, y = cov_time, z = incidence rate)
#if False:
plot_1 = {'x': get_mapped(coverage, "PrEP coverage (%)"),  
          'y': get_mapped(coverage_time, "PrEP coverage time (months)"),
          'z': get_mapped(incidence, "Incidence rate per 100py\n at the end of 5th year")}
# plot heatmap
get_heatplot(plot_1, r"C:\Users\Vijeta\Documents\Projects\Brazil PrEP\Python tool for preparing runs\Sample_plot1.jpg")

#%% second heatplot (x = cov, y = cov_time, z = percentage change in incidence rate)
plot_2 = {'x': get_mapped(coverage, "PrEP coverage (%)"),  
          'y': get_mapped(coverage_time, "PrEP coverage time (months)"),
          'z': get_mapped(incidence_reduction, "Percentage reduction in incidence rate")}
# plot heatmap
get_heatplot(plot_2, r"C:\Users\Vijeta\Documents\Projects\Brazil PrEP\Python tool for preparing runs\Sample_plot2.jpg")

#%% third heatplot

city_grid, cov_grid = np.meshgrid(val['City'], val['PrEPCoverage'])

con_float = np.array([6.97, 5.51, 4.18, 4.10, 4.00, 3.73])
rand_red = deepcopy(con_float)
for i in range(len(val["PrEPCoverage"]) - 1):
    con_float += np.array((i+0.1) * np.ones(len(val["City"])))
    rand_red = np.concatenate([rand_red, con_float])
con_float = [3.03, 3.07, 3.12, 3.13, 3.15, 3.16]
rand_inci = deepcopy(con_float)
for i in range(len(val["PrEPCoverage"]) - 1):
    con_float -= np.multiply(np.true_divide(i+1, 10), np.ones(len(val["City"])))
    rand_inci = np.concatenate([rand_inci, con_float])

city = np.ravel(city_grid)
coverage = np.ravel(cov_grid)
incidence = np.array(rand_inci) 
incidence_reduction = np.array(rand_red)

plot_3 = {'x': get_mapped(coverage, "PrEP coverage (%)"),  
          'y': get_mapped(city, "City"),
          'z': get_mapped(incidence_reduction, "Percentage reduction in incidence rate")}
# plot heatmap
get_heatplot(plot_3, ytick_angle = 45, plot_name = r"C:\Users\Vijeta\Documents\Projects\Brazil PrEP\Python tool for preparing runs\Sample_plot3.jpg")
