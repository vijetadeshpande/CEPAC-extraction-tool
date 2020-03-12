# -*- coding: utf-8 -*-
"""
Created on Fri Sep 20 16:19:37 2019

@author: Vijeta

#%%

This files does following things (basically comparison of CEPAC output
for different set of runs)
1. Read and extract required ouput
2. plot the ouput and compare with static model values
3. collects results in per year format
4. creates an excel file of cepac output (monthly format)

#%%

"""
import scipy as sp
import link_to_cepac_in_and_out_files as link
import pandas as pd
from copy import deepcopy
import os
import numpy as np
import matplotlib.pyplot as plt
import math
from ggplot import ggplot, geom_line, geom_point, aes, facet_wrap, ggtitle, stat_smooth, geom_vline, theme_gray
from mpl_toolkits.mplot3d import Axes3D
import seaborn as sb



#%% AUX functions
def get_in_out_data(path):
    
    cepac_out, cepac_in = {}, {}
    
    # import required input and output
    for k in path:
        cepac_out[k] = link.import_all_cepac_out_files(os.path.join(path[k], r'results'), module = 'regression')
        cepac_in[k] = link.import_all_cepac_in_files(path[k])
# =============================================================================
#     cepac_out['Positive coverage (15%)'] = link.import_all_cepac_out_files(os.path.join(path['positive coverage'], r'results'), module = 'regression')
#     cepac_out['Zero coverage'] = link.import_all_cepac_out_files(os.path.join(path['zero coverage'], r'results'), module = 'regression')
#     cepac_in['Positive coverage (15%)'] = link.import_all_cepac_in_files(path['positive coverage'])
#     cepac_in['Zero coverage'] = link.import_all_cepac_in_files(path['zero coverage'])
# =============================================================================
    # get transmission mutiplier from input file
    var_name = ["DynamicTransmissionNumTransmissionsHRG"]
    for sce in cepac_in:
        for run in cepac_in[sce]:
            cepac_in[sce][run] = link.get_subset_of_in_file(cepac_in[sce][run], var_name)
    
    return cepac_in, cepac_out
#%% 
def get_cepac_out_plot(df, path, horizon):
    
    # path to save images
    folder_name = 'Plots--'
    save_path = os.path.join(path['After incidence reduction'], folder_name)
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    
    # filter data
    df = df.loc[df.loc[:, 'Scenario'] != "Static model values", :]
    
    # plot theme
    #tx_sb = sb.FacetGrid(data = plot_frame, row = 'Scenario')
    sb.set_style("darkgrid", {"axes.facecolor": ".9"})
    sb.set_context("notebook", rc={"lines.linewidth": 0.7})
    
    
    # Transmissions    
    plt.figure()
    df1 = df.loc[df.loc[:, 'Scenario'] != 'Static model values', :]
    # TODO: following line is jugaad to get rid of only ind benefit values, fix it
    #df1 = df1.drop(labels = np.arange(horizon*(2), horizon*(3)), axis = 0)
    #ax_tx_sb = sb.lineplot(x = 't (simulation month)', y = 'Number of transmissions', data = df1,\
    #                    hue = 'Scenario', style = 'Strategy', legend = "full", alpha = 0.9)#, line_kws = {'alpha': 0.5})
    ax_tx_sb = sb.lineplot(x = 't (simulation month)', y = 'Number of transmissions', data = df1,\
                        hue = 'Strategy', legend = "full", alpha = 0.9)#, line_kws = {'alpha': 0.5})
    ax_tx_sb.axvline(x = 30, linestyle = "--", color = "black", alpha = 0.2, label = "PrEP coverage cap")
# =============================================================================
#     #ax_tx_sb = sb.lineplot(x = 't (simulation month)', y = 'Number of transmissions', data = df1,\
#     #                    hue = 'Strategy', legend = "full", alpha = 0.9)#, line_kws = {'alpha': 0.5})
#     #ax_tx_sb.axvline(x = 30, linestyle = "--", color = "black", alpha = 0.2, label = "PrEP coverage cap")
#     #lw = ax_tx_sb.ax.lines[0].get_linewidth()
#     #plt.setp(ax_tx_sb.ax.lines, linewidth=lw)
# =============================================================================
    plt.setp(ax_tx_sb.get_legend().get_texts(), fontsize='6')
    plt.savefig(os.path.join(save_path, r'Number of transmissions'), dpi = 360)
    del ax_tx_sb
    
    # Cumulative transmissions
    plt.figure()
    df11 = df.loc[df.loc[:, 'Scenario'] != 'Static model values', :]
    #ax_tx_sb = sb.lineplot(x = 't (simulation month)', y = 'Number of cumulative transmissions', data = df11,\
    #                    hue = 'Scenario', style = 'Strategy', legend = "full", alpha = 0.9)#, line_kws = {'alpha': 0.5})
    ax_tx_sb = sb.lineplot(x = 't (simulation month)', y = 'Number of cumulative transmissions', data = df11,\
                        hue = 'Strategy', legend = "full", alpha = 0.9)#, line_kws = {'alpha': 0.5})

# =============================================================================
#     #ax_tx_sb = sb.lineplot(x = 't (simulation month)', y = 'Number of cumulative transmissions', data = df11,\
#     #                    hue = 'Strategy', legend = "full", alpha = 0.9)
#     #ax_tx_sb.axvline(x = 30, linestyle = "--", color = "black", alpha = 0.2, label = "PrEP coverage cap")
#     #lw = ax_tx_sb.ax.lines[0].get_linewidth()
#     #plt.setp(ax_tx_sb.ax.lines, linewidth=lw)
# =============================================================================
    ylabels = ['{:,.0f}'.format(x) + 'Mil.' for x in ax_tx_sb.get_yticks()/1000000]
    ax_tx_sb.set_yticklabels(ylabels)
    plt.setp(ax_tx_sb.get_legend().get_texts(), fontsize='6')
    plt.savefig(os.path.join(save_path, r'Number of cumulative transmissions'), dpi = 360)
    del ax_tx_sb
    
    # Infections
    plt.figure()
    #ax_inf_sb = sb.lineplot(x = 't (simulation month)', y = 'Number of incident cases', data = df1,\
    #                hue = 'Scenario', style = 'Strategy', legend = "full", alpha = 0.9)#, line_kws = {'alpha': 0.5})
    ax_inf_sb = sb.lineplot(x = 't (simulation month)', y = 'Number of incident cases', data = df1,\
                    hue = 'Strategy', legend = "full", alpha = 0.9)#, line_kws = {'alpha': 0.5})

# =============================================================================
#     ax_inf_sb = sb.lineplot(x = 't (simulation month)', y = 'Number of incident cases', data = df1,\
#                      hue = 'Strategy', legend = "full", alpha = 0.9)#, line_kws = {'alpha': 0.5})
#     #lw = ax_inf_sb.ax.lines[0].get_linewidth()
#     #plt.setp(ax_inf_sb.ax.lines, linewidth=lw)
# =============================================================================
    ax_inf_sb.axvline(x = 30, linestyle = "--", color = "black", alpha = 0.2, label = "PrEP coverage cap")
    plt.setp(ax_inf_sb.get_legend().get_texts(), fontsize='6')
    plt.savefig(os.path.join(save_path, r'Number of incident cases'), dpi = 360)
    del ax_inf_sb
    
    # cumulative infections
    plt.figure()
    df12 = df.loc[df.loc[:, 'Scenario'] != 'Static model values', :]
    #ax_inf_sb = sb.lineplot(x = 't (simulation month)', y = 'Number of cumulative incident cases', data = df12,\
    #                hue = 'Scenario', style = 'Strategy', legend = "full", alpha = 0.9)#, line_kws = {'alpha': 0.5})
    ax_inf_sb = sb.lineplot(x = 't (simulation month)', y = 'Number of cumulative incident cases', data = df12,\
                    hue = 'Strategy', legend = "full", alpha = 0.9)#, line_kws = {'alpha': 0.5})

# =============================================================================
#     ax_inf_sb = sb.lineplot(x = 't (simulation month)', y = 'Number of cumulative incident cases', data = df12,\
#                     hue = 'Strategy', legend = "full", alpha = 0.9)#, line_kws = {'alpha': 0.5})
#     #lw = ax_inf_sb.ax.lines[0].get_linewidth()
#     #plt.setp(ax_inf_sb.ax.lines, linewidth=lw)
# =============================================================================
    ylabels = ['{:,.0f}'.format(x) + 'Mil.' for x in ax_inf_sb.get_yticks()/1000000]
    ax_inf_sb.set_yticklabels(ylabels)
    plt.setp(ax_inf_sb.get_legend().get_texts(), fontsize='6')
    plt.savefig(os.path.join(save_path, r'Number of cumulative incident cases'), dpi = 360)
    del ax_inf_sb
    
    if False:
        # Transmission rate
        plt.figure()
        df2 = df.loc[:, ['Scenario', 'Strategy', 'Transmission rate (per 100py)', 't (simulation month)']]
        # TODO: following line is jugaad to get rid of only ind benefit values, fix it
        #df2 = df2.drop(labels = np.arange(horizon*(2), horizon*(3)), axis = 0)
        df2 = df2.reset_index(drop = True)
        #ax_tx_rate_sb = sb.lineplot(x = 't (simulation month)', y = 'Transmission rate (per 100py)', data = df2,\
        #                hue = 'Scenario', style = 'Strategy', legend = "full", alpha = 0.9)#, line_kws = {'alpha': 0.5})
        ax_tx_rate_sb = sb.lineplot(x = 't (simulation month)', y = 'Transmission rate (per 100py)', data = df2,\
                        hue = 'Scenario', style = 'Strategy', legend = "full", alpha = 0.9)#, line_kws = {'alpha': 0.5})

# =============================================================================
#     df2.loc[df2.loc[:, 'Scenario'] == 'Static model values', 'Strategy'] = 'Static model values'
#     ax_tx_rate_sb = sb.lineplot(x = 't (simulation month)', y = 'Transmission rate (per 100py)', data = df2,\
#                     hue = 'Strategy', legend = "full", alpha = 0.9)#, line_kws = {'alpha': 0.5})
#     #lw = ax_tx_rate_sb.ax.lines[0].get_linewidth()
#     #plt.setp(ax_tx_rate_sb.ax.lines, linewidth=lw)
# =============================================================================
        ax_tx_rate_sb.axvline(x = 30, linestyle = "--", color = "black", alpha = 0.2, label = "PrEP coverage cap")
        plt.setp(ax_tx_rate_sb.get_legend().get_texts(), fontsize='6')
        plt.savefig(os.path.join(save_path, r'Transmission rate (per 100py)'), dpi = 360)
        del ax_tx_rate_sb

    
    # Incidence rate
        plt.figure()
        df3 = df.loc[:, ['Scenario', 'Strategy', 'Incidence rate (per 100py)', 't (simulation month)']]
        # TODO: following line is jugaad to get rid of only ind benefit values, fix it
        #df3 = df3.drop(labels = np.arange(horizon*(2), horizon*(3)), axis = 0)
        df3 = df3.reset_index(drop = True)
        #ax_inci_rate_sb = sb.lineplot(x = 't (simulation month)', y = 'Incidence rate (per 100py)', data = df3,\
        #                hue = 'Scenario', style = 'Strategy', legend = "full", alpha = 0.9)#, line_kws = {'alpha': 0.5})
        ax_inci_rate_sb = sb.lineplot(x = 't (simulation month)', y = 'Incidence rate (per 100py)', data = df3,\
                        hue = 'Scenario', style = 'Strategy', legend = "full", alpha = 0.9)#, line_kws = {'alpha': 0.5})

# =============================================================================
#     df3.loc[df3.loc[:, 'Scenario'] == 'Static model values', 'Strategy'] = 'Static model values'
#     ax_inci_rate_sb = sb.lineplot(x = 't (simulation month)', y = 'Incidence rate (per 100py)', data = df3,\
#                     hue = 'Strategy', legend = "full", alpha = 0.9)#, line_kws = {'alpha': 0.5})    
#     #lw = ax_inci_rate_sb.ax.lines[0].get_linewidth()
#     #plt.setp(ax_inci_rate_sb.ax.lines, linewidth=lw)
# =============================================================================
        ax_inci_rate_sb.axvline(x = 30, linestyle = "--", color = "black", alpha = 0.2, label = "PrEP coverage cap")
        plt.setp(ax_inci_rate_sb.get_legend().get_texts(), fontsize='6')
        plt.savefig(os.path.join(save_path, r'Incidence rate (per 100py)'), dpi = 360)
        del ax_inci_rate_sb
    
    # ggplot code (much faster than seaborn but I couldn't figure out few things)
    
    # =============================================================================
    # theme = theme_gray()
    # theme._rcParams['axes.labelsize'] = 30
    # tx_plt = ggplot(aes(x = 't (simulation month)', y = 'Number of transmissions', color = 'Strategy'), data = plot_frame) + facet_wrap('Scenario', scales = 'free') + geom_line(alpha = 0.5)# + stat_smooth(method= 'loess', se = False) #+ geom_vline(xintercept = [0, 60, 120, 180, 240], linetype = "dashed")
    # inf_plt = ggplot(aes(x = 't (simulation month)', y = 'Number of infections', color = 'Strategy'), data = plot_frame) + facet_wrap('Scenario', scales = 'free') + geom_line(alpha = 0.5) + theme
    # tx_plt.save('Transmission_plot_(Final from tests + dist over start age + random seed + 30years)', dpi = 700)
    # del tx_plt
    # inf_plt.save('Infections_plot_(Final from tests + dist over start age + random seed + 30years)', dpi = 700)
    # del inf_plt
    # 
    # =============================================================================
    
    return
#%%
def get_static_model_rates(horizon):
    ref_val = np.zeros((1200,2))
    # following values are calculated from the input values for incidence and contact rate
    ref_val[0:360, 0] = 5.20
    ref_val[360:468, 0] = 5.81
    ref_val[468: , 0] = 1.21
    # following values are from incidence rate data
    ref_val[0:360, 1] = 4.3
    ref_val[360:468, 1] = 4.8
    ref_val[468: , 1] = 1    
    theta_prev_bar = np.zeros((horizon, 2))
    total_sample = 10**1
    for i in range(0,total_sample):
        age = -1
        while age < 0 or age >= (1200 - horizon):
            age = math.floor(np.random.normal(381.60, 108)) # mean and sd are from input data
        theta_n = ref_val[age:age+horizon, :]

        # robbins-monroe stochastic approximation
        theta_n_bar = (1 - 1/(i+1)) * theta_prev_bar + (1/(i+1)) * theta_n
        theta_prev_bar = theta_n_bar
        
        # print progress
        if (i%(total_sample/10)) == 0:
            print(('Simulation is %d percent complete')%(i*100/total_sample))
        
    
    return theta_n_bar
#%%
def get_run_name(run):
    
    if 'SQ' in run or 'INT' in run or 'intervention' in run:
        name = (('SQ' in run) * ['SQ'] + ('INT' in run or 'intervention' in run) * ['Intervention'])[0]
        if "DTM" in run:
            name = "Intervention w/o DTM" #(Disabled: DTM,\nEnabled: Inci. reduction, PrEP)"
        elif "woIR" in run:
            name = "Intervention w/o indirect incidence reduction" #(Disabled: Inci. reduction,\nEnabled: DTM, PrEP)"
        elif "woPrEP" in run:
            name = "Intervention w/o direct incidence reduction"# (Disabled: PrEP,\nEnabled: DTM, Inci. red.)"
        else:
            name = name
    else:
        name = ((run == 'A') * ['SQ'] + (run == 'B') * ['Intervention \n(Direct individual and indirect \ncommunity benefit)'] + (run == 'C') * ['Intervention \n(Only direct individual benefit)'])[0]
        
    return name
#%% EXTRACT AND COMPARE TRANSMISSION OUTPUT OF CEPAC

# path to import files
path = {}
#path['Before incidence reduction'] = r'C:\Users\Vijeta\Documents\Projects\Brazil PrEP\Transmission runs\Input files\Runs asked by Ken\Final runs'
path['After incidence reduction'] = r'C:\Users\Vijeta\Documents\Projects\Brazil PrEP\Transmission runs\Input files\Runs asked by Ken\Final runs'

# define some hard inputs
#start_age = 20*12
horizon = 60

# get data
cepac_in, cepac_out = get_in_out_data(path)

# collect results to plot
total_keys = 0
for k in cepac_out:
    total_keys += len(cepac_out[k])
    total_keys -= 1 # for popstats
plot_frame = pd.DataFrame(0, index = np.arange(horizon*(total_keys + 2)), columns = ['Scenario'])
row = 0
for sce in cepac_out:
    if sce == 'datum':
        continue
    else:
        for run in cepac_out[sce]:
            if run == 'popstats':
                continue
            else:
                row += 1
            # 
            plot_frame.loc[(row-1)*horizon:(row-1)*horizon + horizon-1, 'Number of transmissions'] = cepac_out[sce][run]['transmissions'].iloc[0:horizon].values
            plot_frame.loc[(row-1)*horizon:(row-1)*horizon + horizon-1, 'Number of cumulative transmissions'] = plot_frame.loc[(row-1)*horizon:(row-1)*horizon + horizon-1, 'Number of transmissions'].cumsum()
            plot_frame.loc[(row-1)*horizon:(row-1)*horizon + horizon-1, 'Number of incident cases'] = cepac_out[sce][run]['infections'].iloc[0:horizon].values
            plot_frame.loc[(row-1)*horizon:(row-1)*horizon + horizon-1, 'Number of cumulative incident cases'] = plot_frame.loc[(row-1)*horizon:(row-1)*horizon + horizon-1, 'Number of incident cases'].cumsum()
            plot_frame.loc[(row-1)*horizon:(row-1)*horizon + horizon-1, 'Transmission rate (per 100py)'] = float(cepac_in[sce][run]['DynamicTransmissionNumTransmissionsHRG'].iloc[0, 1]) * cepac_out[sce][run]['multiplier'].iloc[0:horizon].values
            plot_frame.loc[(row-1)*horizon:(row-1)*horizon + horizon-1, 'Incidence rate (per 100py)'] = 1200*(cepac_out[sce][run]['infections'].iloc[0:horizon].values/cepac_out[sce][run]['susceptibles'].iloc[0:horizon].values)
            plot_frame.loc[(row-1)*horizon:(row-1)*horizon + horizon-1, 't (simulation month)'] = np.arange(0, horizon)# + 240
            plot_frame.loc[(row-1)*horizon:(row-1)*horizon + horizon-1, 'Strategy'] = run#get_run_name(run)
            plot_frame.loc[(row-1)*horizon:(row-1)*horizon + horizon-1, 'Scenario'] = sce
            
plot_frame.loc[horizon*total_keys: horizon*(total_keys + 1), 'Scenario'] = 'Static model values'
plot_frame.loc[horizon*(total_keys+1): horizon*(total_keys + 2), 'Scenario'] = 'Static model values'
static_rates = get_static_model_rates(horizon)
for i in [0, 1]:
    plot_frame.loc[horizon*(total_keys + i): horizon*(total_keys + i + 1) - 1, 'Transmission rate (per 100py)'] = static_rates[:,0]
    plot_frame.loc[horizon*(total_keys + i): horizon*(total_keys + i + 1) - 1, 'Incidence rate (per 100py)'] = static_rates[:,1]
    plot_frame.loc[horizon*(total_keys + i): horizon*(total_keys + i + 1) - 1, 'Strategy'] = ((i ==  0) * ['SQ']  + (i ==  1) * ['Intervention'])[0]
    plot_frame.loc[horizon*(total_keys + i): horizon*(total_keys + i + 1) - 1, 't (simulation month)'] = np.arange(0, horizon)

#%% PLOT: transmissions, infections and multiplier 
get_cepac_out_plot(plot_frame, path, horizon)

#%% calculate relative difference rates
# TODO: following line is jugaad to get rid of only ind benefit values, fix it
#plot_diff = plot_frame.drop(labels = np.arange(horizon*(2), horizon*(3)), axis = 0)
#plot_diff = plot_diff.loc[plot_diff.loc[:, 'Scenario'] != 'Static model values', :]

#perc_decline_i = (plot_diff.loc[plot_diff.loc[:, 'Scenario'] == 'Before incidence reduction', 'Incidence rate (per 100py)'].values - plot_diff.loc[plot_diff.loc[:, 'Scenario'] == 'After incidence reduction', 'Incidence rate (per 100py)'].values)/(plot_diff.loc[plot_diff.loc[:, 'Scenario'] == 'Before incidence reduction', 'Incidence rate (per 100py)'].values)

#%% Collect results for building tables
total_r = int(horizon*2/2)
collect_result = {}
collect_result['transmissions'] = pd.DataFrame(0, index = np.arange(total_r), columns = ['A', 'B', 'C'])
collect_result['infections'] = pd.DataFrame(0, index = np.arange(total_r), columns = ['A', 'B', 'C'])
collect_result['cumulative transmissions'] = pd.DataFrame(0, index = np.arange(total_r), columns = ['A', 'B', 'C'])
collect_result['cumulative infections'] = pd.DataFrame(0, index = np.arange(total_r), columns = ['A', 'B', 'C'])
collect_result['susceptibles'] = pd.DataFrame(0, index = np.arange(total_r*2), columns = ['A', 'B', 'C'])
collect_result['incidence rate'] = pd.DataFrame(0, index = np.arange(total_r*2), columns = ['A', 'B', 'C'])

row = -1
for sce in cepac_out:
    if sce == 'datum':
        continue
    else:
        row += 1
        for run in cepac_out[sce]:
            if run == 'popstats':
                continue
            #
            row_i = 0
            for i in range(0, horizon, 12):
                idx_start = int(row*horizon) + i
                idx_end = int(idx_start + 11)
                collect_result['transmissions'].loc[row_i + row*int(total_r/12), run] = cepac_out[sce][run]['transmissions'].iloc[i:i + 12].sum()
                collect_result['infections'].loc[row_i + row*int(total_r/12), run] = cepac_out[sce][run]['infections'].iloc[i:i + 12].sum()
                collect_result['susceptibles'].loc[idx_start : idx_end, run] = cepac_out[sce][run]['susceptibles'].iloc[i:i + 12].values
                collect_result['incidence rate'].loc[idx_start : idx_end, run] = 1200 * cepac_out[sce][run]['infections'].iloc[i:i + 12].values/cepac_out[sce][run]['susceptibles'].iloc[i:i + 12].values
                row_i += 1

            collect_result['cumulative transmissions'].loc[(row_i - 30)*(30*row): (row_i - 30)*(30*row) + (row_i - 1), run] = collect_result['transmissions'].loc[(row_i - 30)*(30*row): (row_i - 30)*(30*row) + (row_i - 1), run].cumsum()
            collect_result['cumulative infections'].loc[(row_i - 30)*(30*row): (row_i - 30)*(30*row) + (row_i - 1), run] = collect_result['infections'].loc[(row_i - 30)*(30*row): (row_i - 30)*(30*row) + (row_i - 1), run].cumsum()

#%% write results to excel file

# Create a Pandas Excel writer using XlsxWriter as the engine.
file_name = os.path.join(os.path.join(path['After incidence reduction']), "CEPAC_all_extracted_output.xlsx")
writer = pd.ExcelWriter(file_name, engine='xlsxwriter')

# Write each dataframe to a different worksheet
export_data_dict = {}
for var in cepac_out['After incidence reduction']["PrEP disabled"]:
    export_data_dict[var] = pd.DataFrame()
    
for run in cepac_out['After incidence reduction']:
    for var in cepac_out['After incidence reduction'][run]:
        export_data_dict[var][run] = cepac_out['After incidence reduction'][run][var]
        
for var in export_data_dict:
    export_data_dict[var].to_excel(writer, sheet_name = var)
writer.save()


