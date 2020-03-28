#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 24 12:28:04 2020

@author: vijetadeshpande
"""
from copy import deepcopy
import pandas as pd
import numpy as np
import re

def get_non_na_columns(index, in_file):
    
    # if index is empty return empty columns
    if index == []:
        return []
    
    # extract row corresponding to the index and get columns which are non-NA
    row = in_file.iloc[index]
    if not isinstance(row, pd.Series):
        row = row.iloc[0]
    row = row.dropna()
    cols = row.index.values
    
    # find starting index of a value
    for s_idx in cols:
        if row.iloc[s_idx].isalpha():
            continue
        elif row.iloc[s_idx].isdigit():
            break
        else:
            parts = row.iloc[s_idx].split('.')
            cond = True
            for i in parts:
                i = re.sub(r'E-', '', i)
                cond = (cond and i.isdigit())
            if cond:
                break
            else:
                continue
    
    # only return column number which contain numbers only
    cols = cols[s_idx:]
    
    return cols

def search_var(var, in_file):
    
    # get row
    idxs = in_file.index[in_file[0] == var].values
    
    # check len
    '''
    if len(idx) > 1:
        print('\nThe mentioned variable appears more than once in .in file. All values will be changed if you proceed')
        proceed = input('\nDo you want to proceed (y/n)?')
        if proceed in ['n', 'no', 'N']:
            return
    '''
    
    # get non-NA columns (these colums will only correspon to values not variable name)
    cols = []
    for idx in idxs:
        col = get_non_na_columns(idx, in_file)
        cols.append(col)
    
    # update out_dict
    out_dict = {'index': idxs,'columns': cols}
    
    return out_dict

def expand_value_to_array(val, columns):
    val_expanded = val * np.ones(len(columns))
    
    return val_expanded

def read_values(var, in_file, position = {}):
    
    # avoid mutability
    in_file = deepcopy(in_file)
    
    # get index and column values to replace
    if position == {}:
        position = search_var(var, in_file)
    
    # from position, extract value of variable
    if not isinstance(position['index'], (int, np.int64)):
        val = []
        for row in position['index']:
            row_idx = np.where(position['index'] == row)[0][0]
            row_val = in_file.iloc[row, position['columns'][row_idx]].values
            val.append(row_val)
    else:
        val = in_file.iloc[position['index'], position['columns']].values
    
    # convert values to float
    # TODO: if the currebt variable appears more than once, we take only the first array
    # NEED TO FIX THIS
    val = np.array(val[0]).astype(np.float)
    
    return val

def replace_values(var, val, in_file, position = {}, expand_values = True):
    
    # avoid mutability
    in_file = deepcopy(in_file)
    
    # get index and column values to replace
    if position == {}:
        position = search_var(var, in_file)
        
    # check if variable is present or not
    if position['index'].size == 0:
        print('\nVariable not found in .in file. Nothing is changed in .in file.')
        return in_file
    
    #
    idx = 0
    for row in position['index']:
        cols = position['columns'][idx]
        # check size of the value input and the columns
        len_of_input = 0
        if isinstance(val, float) or isinstance(val, int):
            len_of_input = 1
        else:
            len_of_input = len(val)
        size_match = (len_of_input == len(cols))
        
        # check sizes       
        if (not size_match) and (expand_values):
            val = expand_value_to_array(val, cols)
        
        # replace
        in_file.loc[row, cols] = val
        
        #
        idx += 1
    
    return in_file


