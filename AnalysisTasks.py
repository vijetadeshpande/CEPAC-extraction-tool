#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 23 13:05:30 2020

@author: vijetadeshpande
"""

import os
import sys
import pandas as pd
import link_to_cepac_in_and_out_files as link
import TextFileOperations as t_op
import cluster_operations as c_op
import numpy as np
from copy import deepcopy

class FileChange:
    def __init__(self, file_path, save_path, value_map):
        # check if value map is a dictionary
        if not isinstance(value_map, dict):
            raise TypeError('The input value_map must be a python dictionary')
            return
        
        # set attributes
        self.save_path = save_path
        self.base_in_file = link.read_cepac_in_file(file_path)
        self.var_list = np.array(value_map.keys())
        self.value_map = value_map
        
        # save variable positions in .in file
        position = {}
        for var in self.var_list:
            position[var] = t_op.search_var(var, self.base_in_file)
        self.var_pos = position
    
    def create_in_files(self):
        
        # get list of var to replace, value and base in file
        var_list = self.var_list
        val_map = self.value_map
        in_file = deepcopy(self.base_in_file)
        
        for var in var_list:
            # var should be string
            if not isinstance(var, str):
                raise TypeError('The each key of value map should be string, string of CEPAC variable name')
            
            # replace variable value
            in_file = t_op.replace_values(var, val_map[var], in_file, position = self.var_pos[var])
            
            # TODO: search dependencies of current variable and change those values
            # in_file = find and replace dependent variables
        
        # after we are done changing values for all variables, save .in file
        file_name = os.path.join(self.save_path, 'NewInputFile.in')
        link.write_cepac_in_file(file_name, in_file)
        
        return

             
class OneWaySA:
    def __init__(self, file_path, save_path, value_map):
        # check if value map is a dictionary
        if not isinstance(value_map, dict):
            raise TypeError('The input value_map must be a python dictionary')
            return
        
        # there should be only one variable in value map
        if not len(value_map.keys()) == 1:
            raise ValueError('value_map input to the OneWaySA class should contain only one variable')
            return
        
        # set attributes
        self.var_list = np.array(value_map.keys())
        self.val_list = value_map[self.var[0]]
        self.save_path = os.path.join(save_path, 'OWSA_on var = '+ self.var_list[0])
        self.base_in_file = link.read_cepac_in_file(file_path)
        
        # save variable positions in '.in' file
        position = {}
        for var in self.var_list:
            position[var] = t_op.search_var(var, self.base_in_file)
        self.var_pos = position
    
    def create_in_files(self, parallel = 1):
        
        # get list of var to replace, value and base in file
        var = self.var[0]
        val_list = self.val_list
        in_file = deepcopy(self.base_in_file)
        
        # loop over values we have for var
        for val in val_list:
            # this val can either be a float or array
            if not (isinstance(val, float) or isinstance(val, int) or isinstance(val, np.array)):
                raise TypeError('The value of variable for OWSA must be np.array/float/int')
                return
            
            # replace variable value
            in_file = t_op.replace_values(var, val, in_file, position = self.var_pos[var])
            
            # TODO: search dependencies of current variable and change those values
            # in_file = find and replace dependent variables
            
            # save file
            x = ('OWSA_' + var + '=%.4f' + '.in')%(val)
            file_name = os.path.join(self.save_path, x)
            link.write_cepac_in_file(file_name, in_file)
        
        # parallelize the files
        c_op.parallelize_input(self.save_path, parallel)
        
        return


class TwoWaySA:
    def __init__(self, file_path, save_path, value_map):
        # check if value map is a dictionary
        if not isinstance(value_map, dict):
            raise TypeError('The input value_map must be a python dictionary')
            return
        
        # there should be only one variable in value map
        if not len(value_map.keys()) == 2:
            raise ValueError('value_map input to the TwoWaySA class should contain only two variables')
            return
        
        # set attributes
        self.var_list = np.array(value_map.keys())
        self.val_map = value_map
        self.save_path = os.path.join(save_path, 'TWSA_on var1 = '+ self.var_list[0] + ' and var2 = ' + self.var_list[1])
        self.base_in_file = link.read_cepac_in_file(file_path)
        
        # save variable positions in '.in' file
        position = {}
        for var in self.var_list:
            position[var] = t_op.search_var(var, self.base_in_file)
        self.var_pos = position
        
    def create_in_files(self, parallel = 1):
        
        # get variable list, value map and base in_file
        var_list = self.var_list
        var0, var1 = var_list[0], var_list[1]
        val_map = self.val_map
        in_file = deepcopy(self.base_in_file)
        
        # first start loop over var1 values
        for var0_val in val_map[var0]:
            # this val can either be a float or array
            if not (isinstance(var0_val, float) or isinstance(var0_val, int) or isinstance(var0_val, np.array)):
                raise TypeError('The value of variable for OWSA must be np.array/float/int')
                return
            
            # replace variable value
            in_file = t_op.replace_values(var0, var0_val, in_file, position = self.var_pos[var0])
            
            # TODO: find and replace dependent variables of var0
            
            
            # now start loop over var2
            for var1_val in val_map[var1]:
                # this val can either be a float or array
                if not (isinstance(var0_val, float) or isinstance(var0_val, int) or isinstance(var0_val, np.array)):
                    raise TypeError('The value of variable for OWSA must be np.array/float/int')
                    return
                
                # replace variable value
                in_file = t_op.replace_values(var1, var1_val, in_file, position = self.var_pos[var1])
                
                # TODO: find and replace dependent variables of var1
                
                # save in file
                x = ('TWSA_' + var0 + '=%.4f_' + var1 + '=%.4f' '.in')%(var0_val, var1_val)
                file_name = os.path.join(self.save_path, x)
                link.write_cepac_in_file(file_name, in_file)
        
        # parallize 
        c_op.parallelize_input(self.save_path, parallel)
        
        return
        
        
        
        
        
        
        
        
    
        
        