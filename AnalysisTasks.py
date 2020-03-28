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
import DependentVarList as DepList
from DependentVarList import DepData as DepD
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
        
        # import in file
        self.base_in_file = link.read_cepac_in_file(file_path)
        
        ## fill in missing data required for calculation of dependent variable
        dep_data_map = DepD().fill_blank_data(value_map, self.base_in_file)
        
        # set attributes
        self.var_list = [i for i in value_map.keys()]
        self.val_list = [value_map[i] for i in self.var_list]
        self.val_map = value_map
        self.dep_data_map = dep_data_map
        self.save_path = os.path.join(save_path, 'OWSA_on var = '+ self.var_list[0])
        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)
        
        # save variable positions in '.in' file
        position = {}
        for var in self.var_list:
            position[var] = t_op.search_var(var, self.base_in_file)
        self.var_pos = position
        
        
    def create_in_files(self, parallel = 1):
        
        # get list of var to replace, value and base in file
        var_list = self.var_list
        val_map = self.val_map
        in_file = deepcopy(self.base_in_file)
        
        # loop over values we have for var
        for var in var_list:
            for val in val_map[var]:
                # this val can either be a float or array
                if not (isinstance(val, float) or isinstance(val, int) or isinstance(val, np.array)):
                    raise TypeError('The value of variable for OWSA must be np.array/float/int')
                    return
                
                # replace variable value
                in_file = t_op.replace_values(var, val, in_file, position = self.var_pos[var])
                
                # TODO: search dependencies of current variable and change those values
                in_file = self.dep_data_object.replace_dep_value(var, val, self.dep_data_map, in_file, self.var_pos[var])
                
                # save file
                x = ('%s=%.4f.in')%(var, val)
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
        
        # import in file
        self.base_in_file = link.read_cepac_in_file(file_path)
        
        # fill in missing data required for calculation of dependent variable
        dep_data_object = DepD()
        dep_data_map = dep_data_object.fill_blank_data(value_map, self.base_in_file)
        
        # list of var in analysis
        self.var_list = [i for i in value_map.keys()]
        
        # list of unique dependent vars
        dep_var_list = []
        for var in self.var_list:
            try: 
                dv_list = dep_data_object.get_list_of_dep_variables(var)
            except KeyError:
                continue
            for dv in dv_list:
                if not dv in dep_var_list:
                    dep_var_list.append(dv)
        self.dep_var_list = dep_var_list
        
        # set attributes
        self.val_list = [value_map[i] for i in self.var_list]
        self.val_map = value_map
        self.dep_data_map = dep_data_map
        self.dep_data_object = dep_data_object
        self.save_path = os.path.join(save_path, ('TWSA_var1=%s_var2=%s')%(self.var_list[0], self.var_list[1]))
        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)
        
        # save variable positions in '.in' file
        position = {}
        for var in self.var_list:
            position[var] = t_op.search_var(var, self.base_in_file)
        for var in self.dep_var_list:
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
                raise TypeError('The value of variable for TWSA must be np.array/float/int')
                return
            
            # replace variable value
            in_file = t_op.replace_values(var0, var0_val, in_file, position = self.var_pos[var0])
            
            # TODO: find and replace dependent variables of var0
            in_file = self.dep_data_object.replace_dep_value(var0, var0_val, self.dep_data_map, in_file, self.var_pos)
            
            # now start loop over var2
            for var1_val in val_map[var1]:
                # this val can either be a float or array
                if not (isinstance(var0_val, float) or isinstance(var0_val, int) or isinstance(var0_val, np.array)):
                    raise TypeError('The value of variable for TWSA must be np.array/float/int')
                    return
                
                # replace variable value
                in_file = t_op.replace_values(var1, var1_val, in_file, position = self.var_pos[var1])
                
                # TODO: find and replace dependent variables of var1
                in_file = self.dep_data_object.replace_dep_value(var1, var1_val, self.dep_data_map, in_file, self.var_pos)
                
                # save in file
                x = ('%s=%.4f_%s=%.4f.in')%(var0, var0_val, var1, var1_val)
                file_name = os.path.join(self.save_path, x)
                link.write_cepac_in_file(file_name, in_file)
        
        # parallelize 
        c_op.parallelize_input(self.save_path, parallel)
        
        return
        
        
        
        
        
        
        
        
    
        
        