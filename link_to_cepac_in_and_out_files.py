# -*- coding: utf-8 -*-
"""
Created on Wed Jul  3 15:23:32 2019

@author: Vijeta
"""

import pandas as pd
import numpy as np
import glob
import os
from copy import deepcopy
import re
import adjustments_for_cepac_in_and_out_files as adjust
import dynamic_transmissions_module as dtm
import calculations_for_dependent_variable as dvar
import sys

def import_transmission_inputs_file(path):
    # which extension
    extensions = [r'\*.xlsx']
    #data        = {'input': {}}
    for ex in extensions:
        for filename in glob.glob(path + ex):
            float_df = pd.read_excel(filename, sheet_name='Sheet1')
            
    # adjustments
    cols = float_df.columns.dropna()
    rows = float_df.iloc[:, 0].dropna()
    float_df = float_df.rename_axis(axis = 0, mapper = rows)
    skip_loop = np.where(cols.str.findall(pat = r'^Unnamed:'))
    
    # structurize the data
    d_out = {}
    for i in rows:
        d_out[i] = {}
        for j in range(len(cols)):
            if j in skip_loop[0]:
                continue
            key = cols[j]
            if key in {'Distribution over viral load strata in high-risk group 1','Generic rates of transmission according to viral load strata'}:
                if 'Distribution' in key:
                    float_name = 'dist_vl'
                elif 'Generic rates' in key:
                    float_name = 'rates_attia'
                #    
                d_out[i][float_name] = float_df.loc[i, :][j : j + 6].reset_index(drop = True)
            else:
                if 'Incidence' in key:
                    float_name = 'incidence'
                elif 'HIV infected' in key:
                    float_name = 'n_hiv_pos'
                elif 'HIV uninfected' in key:
                    float_name = 'n_hiv_neg'
                else:
                    print('Arrggghhh, Something is not right in \nfucntion: read_necessary_inputs  \nFile: transmission_algo')
                #    
                d_out[i][float_name] = float_df.loc[i, :][j]
            
    return d_out

def import_perturbation_file(path):
    # setting up perturbation data for sensitivity analysis
    extensions = [r'\*.xlsx']
    # data        = {'input': {}}
    for ex in extensions:
        for filename in glob.glob(path + ex):
            float_df = pd.read_excel(filename, sheet_name=None, header=None)

    # adjust the variable name sheet a bit
    float_df['Variable names'].columns = ['float name', 'variable name', 'dim1', 'dim2']

    return float_df

# TODO: changing (removing backslash) extension for it work on Mac
def import_all_cepac_in_files(path, extensions = [r'*.in']):
    # setting up input data
    #extensions = [r'\*.in']  # ,r'\*.xlsx']
    data = {}
    for ex in extensions:
        for filename in glob.glob(os.path.join(path, ex)):
            if ex == r'*.in':
                float_name = re.sub(r"\.in$", '', os.path.basename(os.path.normpath(filename)))
                with open(filename, 'r') as f2:
                    float_df = pd.DataFrame((f2.read()).split('\n'))
                data[float_name] = float_df[0].str.split(pat=None, n=-1, expand=True)
            elif ex == r'*.xls':
                float_name = re.sub(r"\.xls$", '', os.path.basename(os.path.normpath(filename)))
                data[float_name] = pd.read_excel(filename, sheet_name = None, header = None)

    return data

# TODO: changing (removing backslash) extension for it work on Mac
def import_all_cepac_out_files(path, module = '', sensitivity_module = False, transmission_module = False, extensions = [r'*.out']):
    # define dictionary for saving the output to return
    data = {}
    
    # there will be .txt files also, so, you can iterate over the extensions
    # if you want
    for ex in extensions:
        # read all the files in the folder of the current extension
        for filename in glob.glob(os.path.join(path, ex)):
            if ex == r'*.out':
                float_name = re.sub('.out', "", os.path.basename(os.path.normpath(filename)))
                float_name = re.sub('cepac_run', "", float_name)
                float_name = re.sub('cepac_run,', "", float_name)
                with open(filename, 'r') as f2:
                    float_df = pd.DataFrame((f2.read()).split('\n'))
                float_df = float_df[0].replace(regex = r' ', value = r'_')
                
                if module == 'sensitivity_module':  
                    # TODO: get_subset functions accepts array of variables and not a string of only one var name
                    # following line is computationally expensive
                    if float_name == 'popstats':
                        data[float_name] = float_df.str.split(expand = True)
                    elif not float_name == 'popstats':
                        # subset overall data only
                        data[float_name] = get_subset_of_out_file(float_df, overall = True)
                elif module == 'transmission_module':
                    # TODO: get_subset functions accepts array of variables and not a string of only one var name
                    if not float_name == 'popstats':
                        data[float_name] = {}
                        # get primary transmission data only
                        # varabile to find
                        var = [r'Primary_Transmissions_by_True_HVL_', r'Self_Transmission_Rate_Multiplier' , r'HIV+_Cases_(Incident):']
                        # where to find
                        monthly = True
                        overall = False
                        # take subset of data
                        data[float_name]['transmissions'] = get_subset_of_out_file(float_df, var[0], overall, monthly)
                        
                        # import self transmissions multiplier
                        data[float_name]['multiplier'] = get_subset_of_out_file(float_df, var[1], overall, monthly)
                        
                        # same thing for infections
                        monthly = False
                        overall = True
                        data[float_name]['infections'] = get_subset_of_out_file(float_df, var[2], overall, monthly)
                        
                    elif float_name == 'popstats':
                        data[float_name] = float_df.str.split(expand = True)
                elif module == 'regression':
                    # TODO: test changes made to get_subset
                    # define variables to extract
                    var = [r'Primary_Transmissions_by_True_HVL_', r'Self_Transmission_Rate_Multiplier', r'Incident_Infections', r'HIV-_at_Month_Start']
                    data[float_name] = {}
                    
                    # where to find
                    monthly = True
                    overall = False
                    
                    # take subset of data
                    if 'pop' in float_name:
                        continue
                    
                    # get subset
                    data[float_name] = get_subset_of_out_file(float_df, var, overall, monthly)
                    
                    # key name adjustments
                    name_dict = {"Primary_Transmissions_by_True_HVL_": "transmissions",
                                 "Self_Transmission_Rate_Multiplier": "multiplier",
                                 "Incident_Infections": "infections",
                                 "HIV-_at_Month_Start": "susceptibles"}
                    # TODO: in following loop for replacing the dictionary keys, loop goes over keys twice,
                    # one over all old values and one time over new values. This adds uneccessary computations
                    f_dict = deepcopy(data[float_name])
                    for k in f_dict.keys():
                        data[float_name][name_dict[k]] = data[float_name][k]
                        del data[float_name][k]
                    del f_dict
                else:
                    # if no module name is mentioned, raw data will be the output
                    data[float_name] = float_df

                
            elif ex == r'\*.txt':
                float_name = re.sub('.txt', "", os.path.basename(os.path.normpath(filename)))
                float_name = re.sub('cepac_run', "", float_name)
                float_name = re.sub('cepac_run,', "", float_name)
                with open(filename, 'r') as f2:
                    float_df = pd.DataFrame((f2.read()).split('\n'))
                #x = pd.read_csv(filename, error_bad_lines=False)#, header = None)
                float_df.columns = [0]
                #%%
                # TODO: this section is hardcoding, not sure if it'll work for every file
                #reduce_size_for_experiment = 5000
                float_df_col = float_df.iloc[23: , 0]
                #%% data structurization
                # find indices where new patients are starting
                float_df_full = (float_df_col.str.split(expand = True)).loc[:, :]
                float_df = float_df_full.loc[:, 0:1]
                all_begin_idx = float_df.loc[float_df.loc[:, 0] == 'BEGIN', :].index.values
                all_trans_idx = float_df.loc[float_df[0].str.startswith('**', na = False), :]
                all_death_idx = all_trans_idx.loc[all_trans_idx[1].loc[:] == 'DEATH', 1].index.values
                
                data[float_name] = {}
                pat_sample = -1
                # total_ sample var is for printing progress
                total_sample = len(all_begin_idx)
                for pat in all_begin_idx:
                    pat_sample += 1
                    if pat_sample > len(all_death_idx)-1:
                        break
                    data[float_name][pat_sample] = {'starting condition': {}, 'trajectory': {}}
                    
                    # for transmissions data
                    pat_trans_idx = all_trans_idx.loc[(all_trans_idx.index > pat) * (all_trans_idx.index < all_death_idx[pat_sample])]
                    if sum(pat_trans_idx.index.values) > 1:
                        data[float_name][pat_sample]['trajectory']['non death transmissions'] = float_df_full.loc[pat_trans_idx.index, :]
                    else:
                        data[float_name][pat_sample]['trajectory']['non death transmissions'] = float_df_full.loc[[all_death_idx[pat_sample]], :]
                    
                    # for initialization
                    pat_sample_init = float_df_full.loc[(float_df.index >= all_begin_idx[pat_sample]) * (float_df.index < min(data[float_name][pat_sample]['trajectory']['non death transmissions'].index)), :]
                    x = pd.DataFrame(0, index = [0], columns = ['Gender', 'Age', 'HIV state', 'CHRMS state', 'On PrEP'])
                    x['Gender'] = pat_sample_init.iloc[1,1][:-1]
                    x['Age'] = pat_sample_init.iloc[1,4]
                    x['HIV state'] = pat_sample_init.iloc[3,2]
                    x['CHRMS state'] = pat_sample_init.iloc[5, 3]
                    x['On PrEP'] = pat_sample_init.iloc[4,2]
                    data[float_name][pat_sample]['starting condition'] = x
                    del x
                    
                    # print progress
                    if (pat_sample%(total_sample/10)) == 0:
                        print(('Longitudinal patient data extraction is %d percent complete')%(pat_sample*100/total_sample))
                
                data[float_name]['death transmissions'] = float_df_full.loc[all_death_idx, :]
                #%% Clean object that can be problematic due to mutability
                #data[float_name] = float_df.reset_index(drop = True)
                del float_df
                del float_df_full
                del all_begin_idx
                del all_trans_idx
                del all_death_idx
                
    # adjustments
    if 'out' in ex:
        if 'popstats' in data.keys():
            if not len(data['popstats']) == 0:
                data['popstats'] = adjust.do_adjustments_on_popstats({'popstats': data['popstats']})['popstats']
    else:            
        data = adjust.do_adjustments_on_long_data(data)
        
    return data

def write_cepac_in_file(save_path, df):
    
    # check if input is dataframe
    if not isinstance(df, pd.DataFrame):
        print('\nwrite_cepac_in_file function in link_to_cepac_in_and_out_files.py file requires the input to be in pd.DataFrame format. Current input is not.')
        return False
    
    # adjument for mutability of df
    df = deepcopy(df)
    
    # few adjustments
    df = adjust.do_adjustments_before_printing(df)

    #%% Save file
    df.to_csv(save_path, sep = '\t', na_rep = "", index = False, header = False)

    return

def get_subset_of_in_file(df, var_name = []):
    
    # check if input is dataframe
    if not (isinstance(df, pd.DataFrame) | isinstance(df, pd.Series)):
        print('\nget_subset_of_out_file function in link_to_cepac_in_and_out_files.py file requires the input to be in pd.DataFrame format. Current input is not.')
        return False
    
    df = deepcopy(df)
    
    # iterate over variable names
    #name_dict = {"DynamicTransmissionNumTransmissionsHRG" : "mean transmission rate"}
    out_dict = {}
    for var in var_name:
        if var == "TransmissionRiskMultiplier_T3":
            idx = df.loc[df.loc[:, 0] == var, :].index[0]
            float_df = df.loc[[idx-2, idx-1, idx], :]
            float_df = float_df.reset_index(drop = True)
        else:
            float_df = df.loc[df.loc[:, 0] == var, :]
            float_df = float_df.reset_index(drop = True)
        #float_df = float_df.loc[:, float_df.loc[:,1:] == None]
        out_dict[var] = float_df
        
    return out_dict

def get_subset_of_out_file(df, var_name = [], overall = False, monthly = False):
    
    # check if input is dataframe
    if not (isinstance(df, pd.DataFrame) | isinstance(df, pd.Series)):
        print('\nget_subset_of_out_file function in link_to_cepac_in_and_out_files.py file requires the input to be in pd.DataFrame format. Current input is not.')
        return False
    
    df = deepcopy(df)
    
    if monthly:
        # find the rows where primary transmision values are present
        monthly_data_idx = df[df == r'COHORT_SUMMARY_FOR_MONTH_0'].index.values[0]
        # take a subset 
        df = df.iloc[monthly_data_idx: ]
        df = df.str.split(expand = True)
        df = df.reset_index(drop = True)
        # find rows with primary transmission data
        if not var_name == []:
            out_dict = {}
            for var in var_name:
                idx = df.loc[df.iloc[:,0] == var].index.values
                if var == r'Primary_Transmissions_by_True_HVL_':
                    col_n = 8
                elif var in [r'Self_Transmission_Rate_Multiplier']:
                    col_n = 1
                elif var in [r'Incident_Infections', r'HIV-_at_Month_Start']:
                    col_n = 2 # this value should be = 1, if we want warm-up run values
                else:
                    sys.exit("Variable name in subsetting function in link is not correct")
                
                # adjustments    
                float_df = df.iloc[idx, col_n]
                float_df = float_df.str.strip(r'_')
                float_df = pd.to_numeric(float_df)
                float_df = float_df.reset_index(drop = True)
                
                # store values
                out_dict[var] = float_df
        
    elif overall:
        # find the rows where primary transmision values are present
        overall_data_idx = df[df == r'ART_1_STATS'].index.values[0]
        # take a subset 
        df = df.iloc[0 : overall_data_idx-1].str.split(expand = True)
        df = df.reset_index(drop = True)
        # find variable
        if not var_name == []:
            out_dict = {}
            for var in var_name:
                idx = df.loc[df.iloc[:,0] == var].index.values
                float_df = float(df.iloc[idx, 1].values[0])
                out_dict[var] = float_df
    else:
        out_dict = {}
    
    return out_dict
    
def extract_ind_var_and_val(path):
    
    map_d = [{'y': 'HIVIncidReductionCoefficient', 'x_cepac': ['HIVIncidReductionStopTime'], 'x_user_in': ['percenatge_reduction']},
              {'y': 'PrepIncidMale','x_cepac': ['HIVmthIncidMale'], 'x_user_in': ['prep_efficacy', 'prep_adherence']},
              {'y': 'PrepIncidFemale','x_cepac': ['HIVmthIncidFemale'], 'x_user_in': ['prep_efficacy', 'prep_adherence']},
              {'y': '','x_cepac': [], 'x_user_in': []}]
    
    # list of independed variavles for the dependent ones
    def get_unique_list(x):
        return list(dict.fromkeys(x))
    
    list_of_ind_vars = {'x_cepac': [], 'x_user_in': []}
    for i in range(3):
        for x in map_d[i]['x_cepac']:
            list_of_ind_vars['x_cepac'].append(x)
        for y in map_d[i]['x_user_in']:
            list_of_ind_vars['x_user_in'].append(y)
    list_of_ind_vars['x_cepac'] = get_unique_list(list_of_ind_vars['x_cepac'])
    list_of_ind_vars['x_user_in'] = get_unique_list(list_of_ind_vars['x_user_in'])
    
    # save the values which don't appear in .in file
    cepac_excel = import_all_cepac_in_files(os.path.join(path, r'Input files'), extensions = [r'\*.xls'])
    for a_k in cepac_excel:
        cepac_excel = cepac_excel[a_k]['HIVTest']
        break
    
    ind_var_val = {}
    for i_var in list_of_ind_vars['x_user_in']:
        if 'efficacy' in i_var:
            idx = cepac_excel.loc[cepac_excel.iloc[:, 13] == 'PrEP Efficacy', 13].index.values[0]
            ind_var_val[i_var] = cepac_excel.iloc[idx + 3:idx + 11, [14, 15, 18, 19]].reset_index(drop = True)
        elif 'adherence' in i_var:
            idx = cepac_excel.loc[cepac_excel.iloc[:, 13] == 'PrEP Adherence', 13].index.values[0]
            ind_var_val[i_var] = cepac_excel.iloc[idx + 3:idx + 11, [14, 15, 18, 19]].reset_index(drop = True)
        elif 'percenatge' in i_var:
            idx = cepac_excel.loc[cepac_excel.iloc[:, 9] == 'Total Proportion HIV Incidence Reduction', 9].index.values[0]
            ind_var_val[i_var] = cepac_excel.loc[idx+1, 10]
    
    return list_of_ind_vars, ind_var_val

def calculations_for_depemdent_var(df, dep_indep_var_set, val_in):
    
    df = deepcopy(df)
    
    # what are inputs:
    # df = cepac intervention input file
    # dep_indep_var_set = dictionary of dependent variable and independent 
    # variable. Independent variables should be separated into two keys,
    # 1. inputs available in cepac input file
    # 2. inputs which are not avaialblein cepac input file (requires user input)
    # Therefore, size of the third input i.e. val_in should have the same size as 
    # size odf array mentioned in dep_indep_var_set['x_user_in']
    
    # check if we have all the required inputs
    if not len(dep_indep_var_set['x_user_in']) == len(val_in['x_user_in']):
        print('\n\nlink_to_cepac_in_and_out_files.calculations_for_dependent_var:\n\nOne or more inputs required for calculating dependent variable are abscent')
        return
    
    if val_in['x_cepac'] == {}:
        for ind_var in dep_indep_var_set['x_cepac']:
            val_in['x_cepac'][ind_var] = float(df.loc[df.loc[:, 0] == ind_var, 1: ].dropna(axis=1).values)
    
    #
    df = dvar.calculate_dependent_var_value(df, dep_indep_var_set, val_in)
        
    return df

def extract_input_for_tx_rate_multiplier(path):
    
    # which variables?
    var = {'in file': ['PrEPCoverage', 'CohortSize', 'PrEPDuration', 'HIVmthIncidMale'],
           'excel file': ['prep_efficacy'],
           'other': ['prep_usage_at_initialization']}
    
    #
    if False:
        # read any basecase/intervention .in file (we'll read RunB file)
        parent_dir = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..'))
        file_folder = os.path.join(parent_dir, r'Transmission runs', r'Input files')

        # inputs in .in file
        data = import_all_cepac_in_files(path)
        data = data['B']#['Brazil_RunB']
        input_par = {}
        for v in var['in file']:
            idx = data.loc[data.iloc[:, 0] == v, 0].index.values[0]
            if 'Incid' in v:
                input_par[v] = float(data.loc[idx, :].values[2])
            else:
                input_par[v] = float(data.iloc[idx, :].values[1])
        del data
        # inputs in excel file
        data = import_all_cepac_in_files(file_folder, [r'\*.xls'])
        data = data['Test_RunB']['HIVTest']#['Brazil_RunB']['HIVTest']
        idx = data.loc[data.iloc[:, 13] == 'PrEP Efficacy', 13].index.values[0]
        input_par[var['excel file'][0]] = float(data.iloc[idx + 3, 14])
        # other inputs
        input_par[var['other'][0]] = 'n'
    
    #%%
    cepac_in = import_all_cepac_in_files(path)
    
    # find prep coverage
    for run in cepac_in:
        if "B" in run or "RunB" in run:
            cepac_in = cepac_in[run]
            break

    coverage = cepac_in.loc[cepac_in.loc[:, 0] == "PrEPCoverage", 1].values[0]
    
    input_par = {"CohortSize": 10000000, "HIVmthIncidMale": 0.00357692085607886,
                 "PrEPCoverage": coverage, "PrEPDuration": 60, "prep_efficacy": 0.96, "prep_usage_at_initialization": "n"}
    
    return input_par

def export_output_to_excel(ext_out_path, save_path):
    
    # read all out files in extract out path
    cepac_out = import_all_cepac_out_files(ext_out_path, module = 'regression')
    
    # change structure of the dictionary
    out_dict = {}
    for file in cepac_out:
        if file == 'popstats':
            continue
        for var in cepac_out[file]:
            out_dict[var] = pd.DataFrame()
        break
    for file in cepac_out:
        if file == 'popstats':
            continue
        for var in cepac_out[file]:
            out_dict[var][file] = cepac_out[file][var]
    
    # Create a Pandas Excel writer using XlsxWriter as the engine.
    file_name = os.path.join(save_path, "CEPAC_all_extracted_output.xlsx")
    writer = pd.ExcelWriter(file_name, engine='xlsxwriter')
    
    #
    for var in out_dict:
        out_dict[var].to_excel(writer, sheet_name = var)
    writer.save()
    
    return
    
    