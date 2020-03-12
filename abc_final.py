# -*- coding: utf-8 -*-
"""
Created on Wed Jan  8 11:21:54 2020

@author: Vijeta
"""

import numpy as np
import link_to_cepac_in_and_out_files as link
import os
import pandas as pd
import re
import transmission_algorithm as tx_algo
import matplotlib.pyplot as plt
import seaborn as sb
from copy import deepcopy
import math
#from joblib import Parallel, delayed
import multiprocessing
import abc_auxilliaries as aux

def save_line_plots(plot_dict, save_path):
    
    # what is simulation horizon
    t_sim = 24#120 #60
    
    # plot theme
    #tx_sb = sb.FacetGrid(data = plot_frame, row = 'Scenario')
    #sb.set(font_scale=1.2)
    sb.set_style("darkgrid", {"axes.facecolor": ".9"})
    sb.set_context("notebook", rc={"lines.linewidth": 1}, font_scale = 1.2)
    aspect_r = 1
    line_alpha = 0.9
    colors_r = ["faded green", "windows blue", "amber", "red"]
    colors = ["red", "amber", "windows blue", "faded green"]
    line_palette = sb.xkcd_palette(colors)
    line_palette_r = sb.xkcd_palette(colors_r)
    
    '''
    line_palette = sb.color_palette("deep", n_colors = 4)
    line_palette_r = sb.color_palette("deep", n_colors = 4)
    line_palette_3 = sb.color_palette("muted", n_colors = 3)
    '''
    def get_sq_val_at_last_month(col):
        val = plot_dict['tx and inf'].loc[plot_dict['tx and inf']['Coverage level (%)'] == 0, col].values[t_sim-1]
        return val
    
    # Transmissions
    df = plot_dict['tx and inf']
    df = df.loc[df['Coverage level (%)'].isin([20, 30]), :]    
    plt.figure()
    g = sb.FacetGrid(df, col="Coverage level (%)", aspect = aspect_r)#, hue="Coverage time")#, col_wrap=3)
    g = (g.map(sb.lineplot, "t (simulation month)", "Number of transmissions", "Coverage time (months)", alpha = line_alpha, palette = line_palette_r).add_legend())#, "WellID")
    #ax1, ax2, ax3 = g.axes[0]
    ax1, ax2 = g.axes[0]
    status_quo_tx_val = get_sq_val_at_last_month('Number of transmissions')
    ax1.axhline(status_quo_tx_val, ls='--', color = 'k', alpha = 0.4)
    ax2.axhline(status_quo_tx_val, ls='--', color = 'k', alpha = 0.4)
    #ax3.axhline(status_quo_tx_val, ls='--', color = 'k', alpha = 0.4)
    ax1.text(2,status_quo_tx_val-12000, "SQ transmissions \nat t = " + str(t_sim), alpha = 0.5)
    plt.savefig(os.path.join(save_path, r'Transmissions'), dpi = 360)
    del g
    
    # Infections    
    plt.figure()
    g = sb.FacetGrid(df, col="Coverage level (%)", aspect = aspect_r)#, hue="Coverage time")#, col_wrap=3)
    g = (g.map(sb.lineplot, "t (simulation month)", "Number of infections", "Coverage time (months)", alpha = line_alpha, palette = line_palette_r).add_legend())#, "WellID")
    #ax1, ax2, ax3 = g.axes[0]
    ax1, ax2 = g.axes[0]
    status_quo_inf_val = get_sq_val_at_last_month('Number of infections')
    ax1.axhline(status_quo_inf_val, ls='--', color = 'k', alpha = 0.4)
    ax2.axhline(status_quo_inf_val, ls='--', color = 'k', alpha = 0.4)
    #ax3.axhline(status_quo_inf_val, ls='--', color = 'k', alpha = 0.4)
    ax1.text(5,status_quo_inf_val-5000, "SQ infections \nat t = " + str(t_sim), alpha = 0.5)
    #sb.regplot(x=np.array([t_sim]), y=np.array([22183]), scatter=True, fit_reg=False, marker='x',
    #            scatter_kws={"s": 100})
    plt.savefig(os.path.join(save_path, r'Infections'), dpi = 360)
    del g
    
    # incidence rate  
    plt.figure()
    g = sb.FacetGrid(df, col="Coverage level (%)", aspect = aspect_r)#, hue="Coverage time")#, col_wrap=3)
    g = (g.map(sb.lineplot, "t (simulation month)", "Incidence rate (per 100PY)", "Coverage time (months)", alpha = line_alpha, palette = line_palette_r).add_legend())#, "WellID")
    #ax1, ax2, ax3 = g.axes[0]
    ax1, ax2 = g.axes[0]
    status_quo_inci_val = get_sq_val_at_last_month('Incidence rate (per 100PY)')
    ax1.axhline(status_quo_inci_val, ls='--', color = 'k', alpha = 0.4)
    ax2.axhline(status_quo_inci_val, ls='--', color = 'k', alpha = 0.4)
    #ax3.axhline(status_quo_inci_val, ls='--', color = 'k', alpha = 0.4)
    ax1.text(35,status_quo_inci_val-0.3, "SQ incidence \nat t = " + str(t_sim), alpha = 0.5)
    plt.savefig(os.path.join(save_path, r'Incidence rate'), dpi = 360)
    del g
    
    # incidence rate
    df = plot_dict['tx and inf']
    df = df.loc[df['Coverage level (%)'].isin([0, 10, 20, 30]), :] 
    df = df.loc[df['Coverage time (months)'].isin([24, 60]), :]
    plt.figure()
    g = sb.FacetGrid(df, col="Coverage time (months)", aspect = aspect_r)#, hue="Coverage time")#, col_wrap=3)
    g = (g.map(sb.lineplot, "t (simulation month)", "Incidence rate (per 100PY)", "Coverage level (%)", alpha = line_alpha, palette = line_palette).add_legend())#, "WellID")
    plt.savefig(os.path.join(save_path, r'Incidence rate1'), dpi = 360)
    del g
        
    # redefine frame
    df = plot_dict['tx and inf']
    df = df.loc[df['Coverage level (%)'].isin([0, 10, 20, 30]), :]
    df = df.loc[df['Coverage time (months)'].isin([24, 60]), :]
    
    # Transmissions    
    plt.figure()
    g = sb.FacetGrid(df, col="Coverage time (months)", aspect = aspect_r)#, hue="Coverage time")#, col_wrap=3)
    g = (g.map(sb.lineplot, "t (simulation month)", "Number of transmissions", "Coverage level (%)", alpha = line_alpha, palette = line_palette).add_legend())#, "WellID")
    plt.savefig(os.path.join(save_path, r'Transmissions1'), dpi = 360)
    del g
    
    # Infections    
    plt.figure()
    g = sb.FacetGrid(df, col="Coverage time (months)", aspect = aspect_r)#, hue="Coverage time")#, col_wrap=3)
    g = (g.map(sb.lineplot, "t (simulation month)", "Number of infections", "Coverage level (%)", alpha = line_alpha, palette = line_palette).add_legend())#, "WellID")
    plt.savefig(os.path.join(save_path, r'Infections1'), dpi = 360)
    del g


def save_heatmaps(plot_dict, save_path):
    
    # heat plot for final runs
    df = plot_dict["percentage reduction"]
    # surface plot
    percentage_decline = df['Percentage reduction in incidence rate']
    val = {'PrEPCoverage': df['Coverage level (%)'].unique(), 'PrEPDuration': df['Coverage time (months)'].unique()}
    x_grid, y_grid = np.meshgrid(val['PrEPDuration'], val['PrEPCoverage'])
    z_grid = np.array(percentage_decline).reshape(x_grid.shape)
    x = np.ravel(x_grid)
    y = np.ravel(y_grid)
    z = np.array(percentage_decline)
    sb_heatmap = pd.DataFrame()
    sb_heatmap['PrEP coverage time (months)'] = np.floor(x).astype(int)
    sb_heatmap['PrEP coverage (%)'] = np.floor(y).astype(int)
    sb_heatmap['Percentage declination in incidence'] = z
    sb_heatmap = sb_heatmap.sort_values(by = 'PrEP coverage time (months)')
    heatmap_df = pd.pivot(data = sb_heatmap,
                       index = 'PrEP coverage time (months)',
                       columns = 'PrEP coverage (%)',
                       values = 'Percentage declination in incidence')
    
    # choose color theme
    #cmap = cm.get_cmap('RdYlGn')
    cmap = 'PuBu_r' #'Reds'
    #cmap = 'coolwarm'
    #cmap = sb.cm._cmap_r
    #my_col_map = ["#eff3ff", "#bdd7e7", "#6baed6", "#3182bd", "#08519c"] # high point is dark blue
    #my_col_map_r = ["#08519c", "#3182bd", "#6baed6", "#bdd7e7", "#eff3ff"] # high point is white
    #cmap = sb.color_palette(my_col_map_r)
    
    plt.figure(figsize=(10, 5))
    sb.set(font_scale=1.2)
    heatmap_plot = sb.heatmap(heatmap_df, annot = True, fmt = '0.1f', linewidths = 0.2, cmap = cmap, cbar_kws={'label': 'Percentage reduction in incidence rate\n due to both benefits'})
    heatmap_plot.figure.axes[0].invert_yaxis()
    # if we need to rotate the axis ticks
    heatmap_plot.figure.savefig(os.path.join(save_path, 'Percentage reduction in incidence.jpg'))
    
    if False:
        percentage_decline = df['Only direct']
        z_grid = np.array(percentage_decline).reshape(x_grid.shape)
        z = np.array(percentage_decline)
        sb_heatmap['Percentage declination in incidence'] = z
        sb_heatmap = sb_heatmap.sort_values(by = 'PrEP coverage time (months)')
        heatmap_df = pd.pivot(data = sb_heatmap,
                           index = 'PrEP coverage time (months)',
                           columns = 'PrEP coverage (%)',
                           values = 'Percentage declination in incidence')
        plt.figure(figsize=(10, 5))
        sb.set(font_scale=1.2)
        heatmap_plot = sb.heatmap(heatmap_df, annot = True, fmt = '0.2f', linewidths = 0.2, cmap = cmap, cbar_kws={'label': 'Percentage reduction in incidence\n due to only direct benefit'})
        heatmap_plot.figure.axes[0].invert_yaxis()
        # if we need to rotate the axis ticks
        heatmap_plot.figure.savefig(os.path.join(save_heat, 'Reduction in incidence_Direct benefit.jpg'))
        
        #
        percentage_decline = df['Both']
        z_grid = np.array(percentage_decline).reshape(x_grid.shape)
        z = np.array(percentage_decline)
        sb_heatmap['Percentage declination in incidence'] = z
        sb_heatmap = sb_heatmap.sort_values(by = 'PrEP coverage time (months)')
        heatmap_df = pd.pivot(data = sb_heatmap,
                           index = 'PrEP coverage time (months)',
                           columns = 'PrEP coverage (%)',
                           values = 'Percentage declination in incidence')
        plt.figure(figsize=(10, 5))
        sb.set(font_scale=1.2)
        heatmap_plot = sb.heatmap(heatmap_df, annot = True, fmt = '0.2f', linewidths = 0.2, cmap = cmap, cbar_kws={'label': 'Percentage reduction in incidence\n due to both benefit'})
        heatmap_plot.figure.axes[0].invert_yaxis()
        # if we need to rotate the axis ticks
        heatmap_plot.figure.savefig(os.path.join(save_heat, 'Reduction in incidence_Total benefit.jpg'))


def calculate_inci_rate(df_dict):
    # susceptibles
    _sus = (10000000 * np.ones(df_dict['infections'].shape))
    _inf =  df_dict['infections']
    _inf_cumsum = df_dict['infections'].cumsum()
    _sus[1:] -= _inf_cumsum[0:len(_inf_cumsum)-1]
    
    # inci rate
    _inci_rate = 1200 * (_inf/_sus)
    
    return _inci_rate

def calculate_percentage_reduction(df_sq, df_inv, t_sim):
    return 100 * (df_sq.loc[t_sim-1] - df_inv.loc[t_sim-1])/(df_sq.loc[0])

def create_plot_df(cepac_out): 
    
    # what is simulation horizon
    t_sim = 24#120 #60
    
    # calculate incidence rate
    for file in cepac_out:
        cepac_out[file]['incidence rate'] = calculate_inci_rate(cepac_out[file])
        
    # final out dict
    final_out = {'tx and inf': None, 'percentage reduction': None}#, 'intersection of benefits': None}
    
    # df for plotting tx, infection, inci rate output for each month
    # TODO: following line is hard coded: SQ is one coverage level which doesnot 
    # have multiple coverage time. This produced a problem while faceting
    # in plot generation. Hence, I have copied and pasted same values of SQ
    # in different coverage time values
    df = pd.DataFrame(0, index = np.arange(0, (len(cepac_out) + 3)*t_sim), 
                      columns = ['Coverage level (%)', 'Coverage time (months)', 't (simulation month)', 
                                 'Number of infections', 'Number of transmissions', 'Incidence rate (per 100PY)',
                                 'Cumulative number of infections', 'Cumulative number of transmissions'])
    df_per_red = pd.DataFrame(0, index = np.arange(0, len(cepac_out)-1), 
                              columns = ['Coverage level (%), Coverage time (months)',
                                         'Percentage reduction in incidence rate']) 
    # iterate over files
    row_idx = 0
    for file in cepac_out:
        if file == 'SQ':
            continue
        # tx and inf out
        df.loc[row_idx: row_idx + t_sim-1, 't (simulation month)'] = np.arange(0, t_sim)
        df.loc[row_idx: row_idx + t_sim-1, 'Number of infections'] = cepac_out[file]['infections'].loc[0:t_sim-1].values
        df.loc[row_idx: row_idx + t_sim-1, 'Cumulative number of infections'] = cepac_out[file]['infections'].loc[0: t_sim-1].cumsum().values
        df.loc[row_idx: row_idx + t_sim-1, 'Number of transmissions'] = cepac_out[file]['transmissions'].loc[0: t_sim-1].values
        df.loc[row_idx: row_idx + t_sim-1, 'Cumulative number of transmissions'] = cepac_out[file]['transmissions'].loc[0: t_sim-1].cumsum().values
        df.loc[row_idx: row_idx + t_sim-1, 'Incidence rate (per 100PY)'] = cepac_out[file]['incidence rate'].loc[0: t_sim-1].values
        df.loc[row_idx: row_idx + t_sim-1, 'Coverage level (%)'] = aux.get_coverage_level_from_file_name(file)
        df.loc[row_idx: row_idx + t_sim-1, 'Coverage time (months)'] = aux.get_coverage_time_from_file_name(file)
        df_per_red.loc[row_idx/t_sim, 'Coverage level (%)'] = aux.get_coverage_level_from_file_name(file)
        df_per_red.loc[row_idx/t_sim, 'Coverage time (months)'] = aux.get_coverage_time_from_file_name(file)
        df_per_red.loc[row_idx/t_sim, 'Percentage reduction in incidence rate'] = calculate_percentage_reduction(cepac_out['SQ']['incidence rate'], cepac_out[file]['incidence rate'], t_sim)
        #df.loc[row_idx: row_idx + t_sim-1, 'Coverage level (%)'] = 0
        #df.loc[row_idx: row_idx + t_sim-1, 'Coverage time (months)'] = 0
    
        # increase index
        row_idx += t_sim

    # for SQ we'll put same values for all coverage and coverage time values
    # plotting is easier this way
    file = 'SQ'
    for cov_t in df_per_red['Coverage time (months)'].unique():
        # tx and inf out
        df.loc[row_idx: row_idx + t_sim-1, 't (simulation month)'] = np.arange(0, t_sim)
        df.loc[row_idx: row_idx + t_sim-1, 'Number of infections'] = cepac_out[file]['infections'].loc[0:t_sim-1].values
        df.loc[row_idx: row_idx + t_sim-1, 'Cumulative number of infections'] = cepac_out[file]['infections'].loc[0: t_sim-1].cumsum().values
        df.loc[row_idx: row_idx + t_sim-1, 'Number of transmissions'] = cepac_out[file]['transmissions'].loc[0: t_sim-1].values
        df.loc[row_idx: row_idx + t_sim-1, 'Cumulative number of transmissions'] = cepac_out[file]['transmissions'].loc[0: t_sim-1].cumsum().values
        df.loc[row_idx: row_idx + t_sim-1, 'Incidence rate (per 100PY)'] = cepac_out[file]['incidence rate'].loc[0: t_sim-1].values
        df.loc[row_idx: row_idx + t_sim-1, 'Coverage level (%)'] = 0
        df.loc[row_idx: row_idx + t_sim-1, 'Coverage time (months)'] = cov_t
        
        # increase row idx
        row_idx += t_sim
            
    # save df in dict
    df['Coverage time (months)'] = df['Coverage time (months)'].astype('int64')
    final_out['tx and inf'] = df
    final_out['percentage reduction'] = df_per_red
            
    
    return final_out
    

def analyze_final_output(path_inv, path_sq):
    
    # extract cepac out
    cepac_out = link.import_all_cepac_out_files(path_inv, module = 'regression')
    
    # read SQ out
    cepac_out['SQ'] = (link.import_all_cepac_out_files(path_sq, module = 'regression'))['SQ']

    # create a plotting friendly df
    plot_dict = create_plot_df(cepac_out)
    
    # plot results and save images
    # lineplot
    folder_name = 'Line plots for CEPAC output'
    save_path = os.path.join(os.path.join(path_inv, '..', '..'), folder_name)
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    #save_line_plots(plot_dict, save_path)
    # heatmap
    folder_name = 'Heatmaps for CEPAC output'
    save_path = os.path.join(os.path.join(path_inv, '..', '..'), folder_name)
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    save_heatmaps(plot_dict, save_path)