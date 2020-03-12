# -*- coding: utf-8 -*-
"""
Created on Fri Jan  3 13:20:29 2020

@author: Vijeta
"""
"""
THIS FILE READS OUTPUT FILES FOR MULTIPLE A, B AND C RUNS. THESE RUNS ARE 
USED TO CALCULATE PERCENTAGE DECLINATION IN THE INCIDENCE DUE TO COMMUNITY 
BENEFIT OF PrEP. IT BROADLY WORKS AS FOLLOWS:
    
NEW FOLDER FOR FINAL INTERVENTION RUNS (HAVING CALCULATED PERCENTAGE DECLINE 
VALUES FOR RESPECTIVE PAIR OF COVERAGE-COVERAGE TIME) HAVING .in FILE = 
f(PATH FOR RESULTS FROM A,B,C RUNS)

NOTE: THIS FILE MIGHT WORK FOR INTERVENTIONS OTHER THAN PrEP BUT CURRENTLY IT 
ONLY WORKS FOR PrEP.
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
import abc_auxilliaries as aux

def plot_heatmap(val_to_replace, percentage_decline, path_dict):
    
    # surface plot
    x_grid, y_grid = np.meshgrid(val_to_replace['PrEPDuration'], val_to_replace['PrEPCoverage'])
    z_grid = np.array(percentage_decline).reshape(x_grid.shape)
    x = np.ravel(x_grid)
    y = np.ravel(y_grid)
    z = np.array(percentage_decline)
    sb_heatmap = pd.DataFrame()
    sb_heatmap['PrEP coverage time (months)'] = np.floor(x)
    sb_heatmap['PrEP coverage (%)'] = np.floor(y * 100)
    sb_heatmap['Percentage declination in incidence'] = z
    sb_heatmap = sb_heatmap.sort_values(by = 'PrEP coverage time (months)')
    plot_df = pd.pivot(data = sb_heatmap,
                       index = 'PrEP coverage time (months)',
                       columns = 'PrEP coverage (%)',
                       values = 'Percentage declination in incidence')
    
    
    # choose color theme
    #cmap = cm.get_cmap('RdYlGn')
    cmap = 'PuBu' #'Reds'
    #cmap = 'coolwarm'
    #cmap = sb.cm._cmap_r
    my_col_map = ["#eff3ff", "#bdd7e7", "#6baed6", "#3182bd", "#08519c"] # high point is dark blue
    my_col_map_r = ["#08519c", "#3182bd", "#6baed6", "#bdd7e7", "#eff3ff"] # high point is white
    cmap = sb.color_palette(my_col_map_r)
    
    plt.figure(figsize=(10, 5))
    sb.set(font_scale=1.2)
    heatmap_plot = sb.heatmap(plot_df, annot = True, fmt = '0.2f', linewidths = 0.2, cmap = cmap, cbar_kws={'label': 'Percentage reduction in incidence\n due to only community benefit'})
    heatmap_plot.figure.axes[0].invert_yaxis()
    # if we need to rotate the axis ticks
    if False:
        heatmap_plot.set_yticklabels(heatmap_plot.get_yticklabels(), rotation = 45)
    heatmap_plot.figure.savefig(os.path.join(os.path.join(path_dict['output']['intervention'], ".."), 'Percentage declination in incidence.jpg'))
    
    # TODO: name of the city can be given as a title to the image

def export_abc_out_to_excel(cepac_out, structured_out, val_to_replace, path_dict):
    
    # Create a Pandas Excel writer using XlsxWriter as the engine.
    file_name = os.path.join(os.path.join(path_dict['output']['intervention'], ".."), "CEPAC_all_extracted_output.xlsx")
    writer = pd.ExcelWriter(file_name, engine='xlsxwriter')
    
    # Write each dataframe to a different worksheet
    export_data_dict = {}
    for k in structured_out[0]["A"]:
        export_data_dict[k] = pd.DataFrame()
        
    for sce in cepac_out["intervention"]:
        if sce == 'popstats':
            continue
        name = aux.get_digit_for_file_name(sce, val_to_replace)
        end_name = sce.split("_")[1]
        for run in structured_out[name]:
            col_name = str(run) + "_" + str(end_name)
            for var in structured_out[name][run]:
                export_data_dict[var][col_name] = structured_out[name][run][var]
            
    for var in export_data_dict:
        export_data_dict[var].to_excel(writer, sheet_name = var)
    writer.save()


def write_final_runs(value_grid, path_dict):
    
    # aux function for creating final run files
    def get_reduction_coeff(percentage_red, stop_time):
        # reduction coefficient will be as follows
        if ((0.01*percentage_red) < 1) and (percentage_red > 0):
            red_coeff = -1*stop_time/(np.log(1 - (0.01*percentage_red)))
        elif (percentage_red == 0) or (percentage_red == 0.0):
            red_coeff = 10000
        else:
            # this says percentage reduction is almost 100%
            red_coeff = -1*stop_time/np.log(10**-100)
        
        return red_coeff
    
    # check if both inputs are dictionaries
    if not (isinstance(value_grid, dict) or isinstance(path_dict, dict)):
        raise TypeError("Input needs to be in dictionary format.")
        return
    #
    val_to_replace = value_grid
    del value_grid
    
    # import out files
    #out_path = os.path.join(path_dict['output']['intervention'], r'results')
    cepac_out = {}
    for k in path_dict['output']:
        cepac_out[k] = link.import_all_cepac_out_files(os.path.join(path_dict['output'][k], r'results'), module = "regression")
    
    # create sets of runs ABC
    out = {}
    name_map = {}
    for k in cepac_out['intervention']:
        if k == 'popstats':
            continue
        key_name = aux.get_digit_for_file_name(k, val_to_replace)
        name_map[key_name] = k
        if "RunB" in k:
            out[key_name] = {}
            out[key_name]['B'] = cepac_out['intervention'][k]
        elif "RunC" in k:
            out[key_name]['C'] = cepac_out['intervention'][k]
        else:
            continue
    
    # TODO: following value will change according to city, need to take care of this
    inp = {}
    for k in out:
        out[k]['A'] = cepac_out['status quo']['SQ']#['A']
        inp[k] = {'PrEPCoverage': 0, 'prep_efficacy': 0.96, 'CohortSize': 10000000,
           'PrEPDuration': 0, 'HIVmthIncidMale': 0.00357692085607886, 'prep_usage_at_initialization': 'n'}
    
    row_idx = 0
    percentage_decline = []
    for i in val_to_replace['PrEPCoverage']:
        for j in val_to_replace['PrEPDuration']:
            if i == 0.0:
                j_idx = np.where(val_to_replace['PrEPDuration'] == j)[0][0]
                out[j_idx] = {}
                out[j_idx]["A"] = cepac_out["status quo"]["SQ"]
                out[j_idx]["B"] = cepac_out["status quo"]["SQ"]
                out[j_idx]["C"] = cepac_out["status quo"]["SQ"]
                inp[j_idx] = inp[5]
            inp[row_idx]['PrEPCoverage'] = i
            inp[row_idx]['PrEPDuration'] = 600 #60
            percentage_decline.append(tx_algo.get_percentage_decline(out[row_idx], inp[row_idx]))
            row_idx += 1
    
    # plot results
    #plot_heatmap(val_to_replace, percentage_decline, path_dict)
    
    # write results to excel file
    export_abc_out_to_excel(cepac_out, out, val_to_replace, path_dict)
        
    # create directory to write the final run files
    if not os.path.exists(os.path.join(path_dict['input'], 'Final runs')):
        os.makedirs(os.path.join(path_dict['input'], 'Final runs'))
    final_path = os.path.join(path_dict['input'], 'Final runs')
    
    # read one .in file (B, as that is intervention file) and alter following values
    # 1. reduction coefficient
    # 2. disable dynamic transmission module
    
    # import base file for B
    base_int = link.import_all_cepac_in_files(path_dict['input'])
    base_int = base_int['B']
    
    # first we'll find the indices of all the required variables
    idx = {}
    var_list = ["UseHIVIncidReduction", "HIVIncidReductionStopTime", "HIVIncidReductionCoefficient", 
                "UseDynamicTransmission", "PrEPCoverage", "PrEPDuration"]
    for k in var_list:
        idx[k] = base_int.loc[base_int.loc[:, 0] == k, :].index.values
    
    # replace required values
    for run in name_map:
        # deepcopy
        float_int = deepcopy(base_int)
        
        # following value of stop time might not be correct
        float_int.loc[idx["HIVIncidReductionStopTime"], 1] = 480#60#120
        coeff = get_reduction_coeff(percentage_decline[run], float_int.loc[idx["HIVIncidReductionStopTime"], 1].values[0])
        if coeff <= 0:
            # disable incidence reduction 
            float_int.loc[idx["UseHIVIncidReduction"], 1] = 0
            #float_int.loc[idx["HIVIncidReductionCoefficient"], 1] = coeff
        else:
            # enable incidence reduction 
            float_int.loc[idx["UseHIVIncidReduction"], 1] = 1
            float_int.loc[idx["HIVIncidReductionCoefficient"], 1] = coeff
        
        # disable dynamic transmission module
        # TODO: we need to take care that the values for risk multiplier are correct
        float_int.loc[idx["UseDynamicTransmission"], 1] = 0
        
        # replace coverage and coverage time
        float_int.loc[idx["PrEPCoverage"], 1:2] = 0.01*(aux.get_coverage_level_from_file_name(name_map[run]))
        float_int.loc[idx["PrEPDuration"], 1:2] = aux.get_coverage_time_from_file_name(name_map[run])
        
        # write the file
        save_path = os.path.join(final_path, name_map[run].split('_')[1]) + '.in'
        link.write_cepac_in_file(save_path, float_int)
        

    

    
