#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 24 12:28:04 2020

@author: vijetadeshpande
"""
from copy import deepcopy
import pandas as pd
import numpy as np

def get_non_na_columns(index, in_file):
    
    # extract row corresponding to the index and get columns which are non-NA
    row = in_file.loc[index, :]
    cols = row.dropna().columns[1:]
    
    return cols

def search_var(var, in_file):
    
    # get row
    idx = in_file.index[in_file.loc[:, 0] == var, :]
    
    # check len
    if len(idx) > 1 or len(idx) < 1:
        raise KeyError('The mentioned variable is either not present in the .in file or appears more than once.')
        return
    
    # get non-NA columns (these colums will only correspon to values not variable name)
    cols = get_non_na_columns(idx, in_file)
    
    # update out_dict
    out_dict = {'index': idx,'columns': cols}
    
    return out_dict

def expand_values(val, columns):
    val_expanded = val * np.ones(len(columns))
    
    return val_expanded

def replace_values(var, val, in_file, expand_values = True):
    
    # avoid mutability
    in_file = deepcopy(in_file)
    
    # get index and column values to replace
    val_place = search_var(var, in_file)
    
    # check size of the value input and the columns
    size_match = (len(val) == len(val_place['columns']))
    
    # check sizes       
    if (not size_match) and (expand_values):
        val = expand_values(val, val_place['columns'])
    else:
        raise ValueError('Size of variable values do not match the size of values present in CEPAC .in file')
        return
    
    # replace
    in_file.loc[val_place['index'], val_place['columns']] = val
    
    return in_file

def get_dependent_var(var):
    
    
    return

