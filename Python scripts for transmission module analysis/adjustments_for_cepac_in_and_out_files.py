# -*- coding: utf-8 -*-
"""
Created on Fri Jul 26 13:48:29 2019

@author: Vijeta
"""
import pandas as pd
from copy import deepcopy

''' FOLLOWING SECTION HAS SOME HARD CODING, JUST BE CAREFUL ABOUT IT '''

def do_adjustments_before_printing(df):
    
    # check if input is dataframe
    if not isinstance(df, pd.DataFrame):
        print('\nwrite_cepac_in_file function in link_to_cepac_in_and_out_files.py file requires the input to be in pd.DataFrame format. Current input is not.')
        return False
    
    c_df = deepcopy(df)
    del df
    df = c_df
    del c_df
    # Adjustment 1: Opportunistic infection
    # find index(PriorOIHistAtEntry + 1)
    # find index(ProbRiskFactorPrev - 1)    
    # loop between above two indices and make respective adjustments
    start_first_oi = df.index[df.loc[:, 0] == 'PriorOIHistAtEntry'].values[0] + 1
    end_last_oi = df.index[df.loc[:, 0] == 'ProbRiskFactorPrev'].values[0] - 1
    
    for idx in range(start_first_oi, end_last_oi, 7):
        df.loc[idx+1:idx+6, 1:7] = df.loc[idx+1:idx+6, 0:6].values
        df.loc[idx+1:idx+6, 0] = ''
        
    # Adjustment 2: HIVtestDetectCost
    idx = df.index[df.iloc[:, 0] == 'HIVtestDetectCost'].values
    df.loc[idx, 3:5] = df.loc[idx, 1:3].values
    df.loc[idx, 1:2] = ''
    
    return df

def do_adjustments_on_popstats(dict_df_in):
    
    # check if input is dict
    if not isinstance(dict_df_in, dict):
        print('\n input data to do_adjustments_on_popstats function in adjustments_for_cepac.....py, shold be a dictionary')
        return False
    
    # keep only required data in each key of the data dictionary
    dict_df_out = {}
    for var in dict_df_in:
        var_df = dict_df_in[var].drop([0,2], axis = 0)
        var_df = var_df.iloc[:, 0:9]
        var_df = var_df.rename(columns=var_df.iloc[0]).drop(var_df.index[0])
        var_df = var_df.loc[:, ['RUN_NAME_', 'COST_', 'LMs_', 'QALMs_', 'COST/QALY_']]
        var_df = var_df.fillna(0).reset_index(drop = True)
        var_df = var_df.drop([var_df.iloc[:,0].count() - 2, var_df.iloc[:,0].count() - 1], axis = 0)
        if var == 'popstats':
            var_df.loc[var_df['RUN_NAME_'].str.find('basecase') > 0, 'RUN_NAME_'] = 'basecase'
            var_df.loc[var_df['RUN_NAME_'].str.find('intervention') > 0, 'RUN_NAME_'] = 'intervention'
            var_df.index = var_df.loc[:, 'RUN_NAME_'].values
        elif not var in {'Basecase and Intervention', 'basecase', 'intervnetion', 'Basecase', 'Intervention'}:
            var_df['RUN_NAME_'] = var_df['RUN_NAME_'].str.split('=', expand = True).iloc[:, 1]
            var_df = var_df.sort_values(by = ['RUN_NAME_'], axis = 0)
        else:
            var_df.loc[var_df['RUN_NAME_'].str.find('basecase') > 0, 'RUN_NAME_'] = 'basecase'
            var_df.loc[var_df['RUN_NAME_'].str.find('intervention') > 0, 'RUN_NAME_'] = 'intervention'
            var_df.index = var_df.loc[:, 'RUN_NAME_'].values
            
        dict_df_out[var] = var_df
        
    
    return dict_df_out

def do_adjustments_on_long_data(dict_in):
    
    # check if input is dict
    if not isinstance(dict_in, dict):
        print('\n input data to do_adjustments_on_popstats function in adjustments_for_cepac.....py, shold be a dictionary')
        return False
    #
    '''
    dict_out = {}
    for var in dict_in:
        start_idx = dict_in[var].loc[dict_in[var].loc[:, 0] == r"BEGIN PATIENT 1", 1].index.values
        float_df = dict_in[var].iloc[start_idx[0]: , :]
        float_df.loc[float_df.loc[:, 1] == r"\^BEGIN", :].index.values
    '''
    
    return dict_in
        
            