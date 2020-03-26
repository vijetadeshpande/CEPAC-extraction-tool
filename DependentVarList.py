#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 26 10:26:27 2020

@author: vijetadeshpande
"""
import numpy as np
import TextFileOperations as t_op
from copy import deepcopy

dep_map = {'PrEPEfficacy': ['PrepIncidMale', 'PrepIncidFemale'],
           'PrEPAdherence': ['PrepIncidMale', 'PrepIncidFemale'],
           'CommunityViralLoad': []}

var_w_dep = [i for i in dep_map.keys()]

calc_map = {'PrepIncidMale' : ['HIVmthIncidMale', 'PrEPEfficacy', 'PrEPAdherence'],
            'PrepIncidFemale': ['HIVmthIncidFemale', 'PrEPEfficacy', 'PrEPAdherence']}

class VarDependencies:
    def __init__(self):
        self.var_having_dep = var_w_dep
        self.dependent_var_map = dep_map
        self.dep_var_calc_req_map = calc_map
    
    def get_from_user(self, var):
        
        #
        while True:
            print(('\n%s is required in sensitivity analysis and not present in .in file')%(var))
            try:
                a_d = int(input(('Is %s, \n1. An array \n2. A number \nPlease enter answer as 1 or 2: ')%(var)))
            except ValueError:
                print("Incorrect response. Try again!")
            else:
                if not a_d in [1, 2]:
                    print("Incorrect response. Try again!")
                else:
                    break
        
        # take value
        if a_d == 1:
            # size?
            while True:
                try:
                    size = int(input('\nEnter size of array (should be an integer): '))
                except ValueError:
                    print("Incorrect response. Try again!")
                else:
                    break
            
            # values?
            idx = 0
            val = []
            while idx <= size-1:
                # check each value
                while True:
                    try:
                        ele = float(input(('\nEnter element at index %d in array: ')%(idx)))
                    except ValueError:
                        print("Incorrect response. Try again!")
                    else:
                        idx += 1
                        break
                val.append(ele)
        
        else:
            while True:
                try:
                    val = float(input(('\nPlease enter value of variable %s: ')%(var)))
                except ValueError:
                    print("Incorrect response. Try again!")
                else:
                    break
        
        return val
        
    def fill_blank_data(self, val_map, base_in_file):
        
        # loop over the keys of value map
        dep_map_out = {}
        for var in val_map.keys():
            # check if there are any dependent variables for current variable
            try:
                dep_list = dep_map[var]
            except KeyError:
                continue
            
            # if yes, get list of dependent variables
            # loop over dependent variables
            for dep_var in dep_list:
                # check what data is required to calculate the dependent variable
                req_data = calc_map[dep_var]
                # loop over each variable in req_data
                keys_present = dep_map_out.keys()
                for data in req_data:
                    if data in keys_present:
                        continue
                    # check data in .in file
                    pos = t_op.search_var(data, base_in_file)
                    # if data is not present in .in file, take raw input
                    if pos['index'].size == 0:
                        # take raw input
                        val = self.get_from_user(data)
                    else:
                        # read values from .in file
                        val = t_op.read_values(data, base_in_file, position = pos)
                    # add key in the value map
                    dep_map_out[data] = val
        
        return dep_map_out