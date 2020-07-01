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
from matplotlib.font_manager import FontProperties
from matplotlib.ticker import FormatStrFormatter
from matplotlib.ticker import FuncFormatter

#
cohort_size = 10000000
pop_factor = 41728 #{'r': 94104, 's': 41728, 'm': 45937}
def save_scatter_plots(plot_df, save_path):
    xs = [12, 24, 36, 48, 60]
    def format_fn(tick_val, tick_pos):
        if int(tick_val) in xs:
            return int(tick_val)
        else:
            return ''
    
    # new column with 'which target is achieved'
    plot_df['Which target is achieved in 5 years'] = 'None'
    plot_df['Time to max. uptake (years)'] = 0
    plot_df['Time to max. uptake (years)'] = plot_df['Time to max. uptake (years)'].values.astype(int)
    for idx in plot_df.index:
        plot_df['Time to max. uptake (years)'].iloc[idx] = int(plot_df['Time to max. uptake (months)'].iloc[idx])
        if plot_df['Percentage reduction in incidence rate'].iloc[idx] < 50:
            plot_df['Which target is achieved in 5 years'].iloc[idx] = 'None'
        elif plot_df['Percentage reduction in incidence rate'].iloc[idx] < 75:
            plot_df['Which target is achieved in 5 years'].iloc[idx] = '50% reduction in incidence rate'
        else:
            plot_df['Which target is achieved in 5 years'].iloc[idx] = '75% reduction in incidence rate'
    
    # plot
    sb.set_style("dark", {"axes.facecolor": "0.97"})
    #sb.set_context("notebook", rc={"lines.linewidth": 0.1}, font_scale = 1.2)
    fig, ax = plt.subplots()
    #fig.set_figheight(1)
    #fig.set_figwidth(2)
    scatter_plot = sb.scatterplot(plot_df['PrEP uptake (%)'], plot_df['Time to max. uptake (months)'], 
                                          hue = plot_df['Which target is achieved in 5 years'],
                                          s = 300,
                                          legend = False)
    # Put the legend out of the figure
    lgd = plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
    ax.yaxis.set_major_locator(plt.MaxNLocator(4))
    ax.yaxis.set_major_formatter(FuncFormatter(format_fn))
    ax.yaxis.set_major_locator(plt.MaxNLocator(integer = True))
    plt.savefig(os.path.join(save_path, r'Target scatter plot'), 
                bbox_extra_artists=(lgd,), 
                bbox_inches='tight',
                dpi = 720)
    
    return 

def save_line_plots(plot_dict, save_path):
    
    # what is simulation horizon
    t_sim = 60
    
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
        val = plot_dict['tx and inf'].loc[plot_dict['tx and inf']['PrEP uptake (%)'] == 0, col].values[t_sim-1]
        return val
    
    # Transmissions
    df = plot_dict['tx and inf']
    df = df.loc[df['PrEP uptake (%)'].isin([10, 60]), :]    
    plt.figure()
    g = sb.FacetGrid(df, col="PrEP uptake (%)", aspect = aspect_r)#, hue="Coverage time")#, col_wrap=3)
    g = (g.map(sb.lineplot, "t (simulation month)", "Number of transmissions", "Time to max. uptake (months)", alpha = line_alpha, palette = line_palette_r).add_legend())#, "WellID")
    #ax1, ax2, ax3 = g.axes[0]
    ax1, ax2 = g.axes[0]
    status_quo_tx_val = get_sq_val_at_last_month('Number of transmissions')
    ax1.axhline(status_quo_tx_val, ls='--', color = 'k', alpha = 0.4)
    ax2.axhline(status_quo_tx_val, ls='--', color = 'k', alpha = 0.4)
    #ax3.axhline(status_quo_tx_val, ls='--', color = 'k', alpha = 0.4)
    ax1.text(2,37000, "SQ transmissions \nat t = " + str(t_sim), alpha = 0.5)
    plt.savefig(os.path.join(save_path, r'Transmissions'), dpi = 360)
    del g
    
    # Infections    
    plt.figure()
    g = sb.FacetGrid(df, col="PrEP uptake (%)", aspect = aspect_r)#, hue="Coverage time")#, col_wrap=3)
    g = (g.map(sb.lineplot, "t (simulation month)", "Number of infections", "Time to max. uptake (months)", alpha = line_alpha, palette = line_palette_r).add_legend())#, "WellID")
    #ax1, ax2, ax3 = g.axes[0]
    ax1, ax2 = g.axes[0]
    status_quo_inf_val = get_sq_val_at_last_month('Number of infections')
    ax1.axhline(status_quo_inf_val, ls='--', color = 'k', alpha = 0.4)
    ax2.axhline(status_quo_inf_val, ls='--', color = 'k', alpha = 0.4)
    #ax3.axhline(status_quo_inf_val, ls='--', color = 'k', alpha = 0.4)
    ax1.text(5,20000, "SQ infections \nat t = " + str(t_sim), alpha = 0.5)
    #sb.regplot(x=np.array([t_sim]), y=np.array([22183]), scatter=True, fit_reg=False, marker='x',
    #            scatter_kws={"s": 100})
    plt.savefig(os.path.join(save_path, r'Infections'), dpi = 360)
    del g
    
    # incidence rate  
    plt.figure()
    g = sb.FacetGrid(df, col="PrEP uptake (%)", aspect = aspect_r)#, hue="Coverage time")#, col_wrap=3)
    g = (g.map(sb.lineplot, "t (simulation month)", "Incidence rate (per 100PY)", "Time to max. uptake (months)", alpha = line_alpha, palette = line_palette_r).add_legend())#, "WellID")
    #ax1, ax2, ax3 = g.axes[0]
    ax1, ax2 = g.axes[0]
    status_quo_inci_val = get_sq_val_at_last_month('Incidence rate (per 100PY)')
    ax1.axhline(status_quo_inci_val, ls='--', color = 'k', alpha = 0.4)
    ax2.axhline(status_quo_inci_val, ls='--', color = 'k', alpha = 0.4)
    #ax3.axhline(status_quo_inci_val, ls='--', color = 'k', alpha = 0.4)
    ax1.text(5,3, "SQ incidence \nat t = " + str(t_sim), alpha = 0.5)
    plt.savefig(os.path.join(save_path, r'Incidence rate'), dpi = 360)
    del g
    
    # incidence rate
    df = plot_dict['tx and inf']
    df = df.loc[df['PrEP uptake (%)'].isin([0, 10, 20, 30]), :] 
    df = df.loc[df['Time to max. uptake (months)'].isin([24, 60]), :]
    plt.figure()
    g = sb.FacetGrid(df, col="Time to max. uptake (months)", aspect = aspect_r)#, hue="Coverage time")#, col_wrap=3)
    g = (g.map(sb.lineplot, "t (simulation month)", "Incidence rate (per 100PY)", "PrEP uptake (%)", alpha = line_alpha, palette = line_palette).add_legend())#, "WellID")
    plt.savefig(os.path.join(save_path, r'Incidence rate1'), dpi = 360)
    del g
        
    # redefine frame
    df = plot_dict['tx and inf']
    df = df.loc[df['PrEP uptake (%)'].isin([0, 10, 20, 30]), :]
    df = df.loc[df['Time to max. uptake (months)'].isin([24, 60]), :]
    
    # Transmissions    
    plt.figure()
    g = sb.FacetGrid(df, col="Time to max. uptake (months)", aspect = aspect_r)#, hue="Coverage time")#, col_wrap=3)
    g = (g.map(sb.lineplot, "t (simulation month)", "Number of transmissions", "PrEP uptake (%)", alpha = line_alpha, palette = line_palette).add_legend())#, "WellID")
    plt.savefig(os.path.join(save_path, r'Transmissions1'), dpi = 360)
    del g
    
    # Infections    
    plt.figure()
    g = sb.FacetGrid(df, col="Time to max. uptake (months)", aspect = aspect_r)#, hue="Coverage time")#, col_wrap=3)
    g = (g.map(sb.lineplot, "t (simulation month)", "Number of infections", "PrEP uptake (%)", alpha = line_alpha, palette = line_palette).add_legend())#, "WellID")
    plt.savefig(os.path.join(save_path, r'Infections1'), dpi = 360)
    del g

def extract_percentage_decline_value(df, cov, cov_t, z_var):
    cov_idx = df.index[df.loc[:, 'PrEP uptake (%)'] == np.floor(cov)].values
    cov_t_idx = df.index[df.loc[:, 'Time to max. uptake (months)'] == np.floor(cov_t)].values
    idx = set(cov_idx).intersection(set(cov_t_idx)).pop()

    return df.loc[idx, z_var]

def save_heatmaps(plot_dict, save_path, z_var):
    
    # heat plot for final runs
    df = plot_dict["percentage reduction"]
    # surface plot
    df = df.loc[:, ['PrEP uptake (%)', 'Time to max. uptake (months)', z_var]]
    val = {'PrEPCoverage': np.sort(df['PrEP uptake (%)'].unique()), 'PrEPDuration': np.sort(df['Time to max. uptake (months)'].unique())}
    x_grid, y_grid = np.meshgrid(val['PrEPDuration'], val['PrEPCoverage'])
    x = np.ravel(x_grid)
    y = np.ravel(y_grid)
    z = []
    for i in range(len(x)):
        z.append(extract_percentage_decline_value(plot_dict['percentage reduction'], y[i], x[i], z_var))
    sb_heatmap = pd.DataFrame()
    sb_heatmap['Time to max. uptake (months)'] = np.floor(x).astype(int)
    sb_heatmap['PrEP uptake (%)'] = np.floor(y).astype(int)
    sb_heatmap[z_var] = z
    sb_heatmap = sb_heatmap.sort_values(by = 'Time to max. uptake (months)')
    heatmap_df = pd.pivot(data = sb_heatmap,
                       index = 'Time to max. uptake (months)',
                       columns = 'PrEP uptake (%)',
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
    

def calculate_inci_rate(df_dict):
    # susceptibles
    _sus = (cohort_size * np.ones(df_dict['infections'].shape))
    _inf =  df_dict['infections']
    _inf_cumsum = df_dict['infections'].cumsum()
    _sus[1:] -= _inf_cumsum[0:len(_inf_cumsum)-1]
    
    # inci rate
    _inci_rate = 1200 * (_inf/_sus)
    
    return _inci_rate

def calculate_percentage_reduction(df_sq, df_inv, t_sim):
    
    #
    red_sq = (df_sq.loc[0] - df_sq.loc[t_sim-1])/(df_sq.loc[0])
    red_inv = (df_inv.loc[0] - df_inv.loc[t_sim-1])/(df_inv.loc[0])
    
    #
    red1 = 100 * (red_inv - red_sq)
    
    #
    red = 100 * (df_sq.loc[t_sim - 1] - df_inv.loc[t_sim-1])/(df_sq.loc[0])
    
    return red

def calculate_infections_averted(df_sq, df_inv, t_sim):
    
    inf_sq = df_sq.iloc[0:t_sim].sum()
    inf_inv = df_inv.iloc[0:t_sim].sum()
    
    inf_averted = inf_sq - inf_inv
    
    return inf_averted

def create_plot_df(cepac_out, HORIZON = 60): 
    
    # what is simulation horizon
    t_sim = HORIZON
    
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
                      columns = ['PrEP uptake (%)', 'Time to max. uptake (months)', 't (simulation month)', 
                                 'Number of infections', 'Number of transmissions', 'Incidence rate (per 100PY)',
                                 'Cumulative number of infections', 'Cumulative number of transmissions'])
    df_per_red = pd.DataFrame(0, index = np.arange(0, len(cepac_out)-1), 
                              columns = ['PrEP uptake (%)', 'Time to max. uptake (months)',
                                         'Percentage reduction in incidence rate', 'Transmissions averted', 'Infections averted']) 
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
        df.loc[row_idx: row_idx + t_sim-1, 'PrEP uptake (%)'] = aux.get_coverage_level_from_file_name(file)
        df.loc[row_idx: row_idx + t_sim-1, 'Time to max. uptake (months)'] = aux.get_coverage_time_from_file_name(file)
        df_per_red.loc[row_idx/t_sim, 'PrEP uptake (%)'] = aux.get_coverage_level_from_file_name(file)
        df_per_red.loc[row_idx/t_sim, 'Time to max. uptake (months)'] = aux.get_coverage_time_from_file_name(file)
        df_per_red.loc[row_idx/t_sim, 'Percentage reduction in incidence rate'] = calculate_percentage_reduction(cepac_out['SQ']['incidence rate'], cepac_out[file]['incidence rate'], t_sim)
        df_per_red.loc[row_idx/t_sim, 'Transmissions averted'] = int(pop_factor * (calculate_infections_averted(cepac_out['SQ']['transmissions'], cepac_out[file]['transmissions'], t_sim)/cohort_size))
        averted_inf = calculate_infections_averted(cepac_out['SQ']['infections'], cepac_out[file]['infections'], t_sim)
        df_per_red.loc[row_idx/t_sim, 'Infections averted'] = int(pop_factor * averted_inf/cohort_size)
        df_per_red.loc[row_idx/t_sim, 'Infections averted (%)'] = 100 * (averted_inf/cepac_out['SQ']['infections'][0:t_sim].sum())
        #df.loc[row_idx: row_idx + t_sim-1, 'Coverage level (%)'] = 0
        #df.loc[row_idx: row_idx + t_sim-1, 'Coverage time (months)'] = 0
    
        # increase index
        row_idx += t_sim

    # for SQ we'll put same values for all coverage and coverage time values
    # plotting is easier this way
    file = 'SQ'
    for cov_t in df_per_red['Time to max. uptake (months)'].unique():
        # tx and inf out
        df.loc[row_idx: row_idx + t_sim-1, 't (simulation month)'] = np.arange(0, t_sim)
        df.loc[row_idx: row_idx + t_sim-1, 'Number of infections'] = cepac_out[file]['infections'].loc[0:t_sim-1].values
        df.loc[row_idx: row_idx + t_sim-1, 'Cumulative number of infections'] = cepac_out[file]['infections'].loc[0: t_sim-1].cumsum().values
        df.loc[row_idx: row_idx + t_sim-1, 'Number of transmissions'] = cepac_out[file]['transmissions'].loc[0: t_sim-1].values
        df.loc[row_idx: row_idx + t_sim-1, 'Cumulative number of transmissions'] = cepac_out[file]['transmissions'].loc[0: t_sim-1].cumsum().values
        df.loc[row_idx: row_idx + t_sim-1, 'Incidence rate (per 100PY)'] = cepac_out[file]['incidence rate'].loc[0: t_sim-1].values
        df.loc[row_idx: row_idx + t_sim-1, 'PrEP uptake (%)'] = 0
        df.loc[row_idx: row_idx + t_sim-1, 'Time to max. uptake (months)'] = cov_t
        
        # increase row idx
        row_idx += t_sim
        
    # adjustment
    df_per_red.loc[:, ['Transmissions averted', 'Infections averted']] = df_per_red.loc[:, ['Transmissions averted', 'Infections averted']].astype('int')
            
    # save df in dict
    df['Time to max. uptake (months)'] = df['Time to max. uptake (months)'].astype('int64')
    final_out['tx and inf'] = df
    final_out['percentage reduction'] = df_per_red
    
    
    return final_out
    

def analyze_final_output(path_inv, path_sq, HORIZON = 60):
    
    # extract cepac out
    cepac_out = link.import_all_cepac_out_files(path_inv, module = 'regression')
    
    # read SQ out
    cepac_out['SQ'] = (link.import_all_cepac_out_files(path_sq, module = 'regression'))['SQ']

    # create a plotting friendly df
    plot_dict = create_plot_df(cepac_out, HORIZON)
    
    # plot results and save images
    # lineplot
    folder_name = 'Line plots for CEPAC output_' + str(HORIZON)
    save_path = os.path.join(os.path.join(path_inv, '..', '..'), folder_name)
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    #save_line_plots(plot_dict, save_path)
    # heatmap
    folder_name = 'Heatmaps for CEPAC output_' + str(HORIZON)
    save_path = os.path.join(os.path.join(path_inv, '..', '..'), folder_name)
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    save_heatmaps(plot_dict, save_path, 'Percentage reduction in incidence rate')
    save_heatmaps(plot_dict, save_path, 'Infections averted')
    save_heatmaps(plot_dict, save_path, 'Infections averted (%)')
    save_heatmaps(plot_dict, save_path, 'Transmissions averted')
    # scatter
    folder_name = 'Scatter plots for CEPAC output_' + str(HORIZON)
    save_path = os.path.join(os.path.join(path_inv, '..', '..'), folder_name)
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    #save_scatter_plots(plot_dict['percentage reduction'], save_path)
    
    return