#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 24 18:51:23 2020

@author: vijetadeshpande
"""

import numpy as np
import pandas as pd
import TextFileOperations as t_op
import link_to_cepac_in_and_out_files as link
import cluster_operations as c_op
from copy import deepcopy
import os
import scipy as sp

parameters = {'attia': np.array([9.03, 8.12, 8.12, 4.17, 2.06, 0.16, 0, 62.56]),
              'viral load distribution off ART': np.array([0.4219, 0.1956, 0.1563, 0.1201, 0.0825, 0.0235, 0.0000, 0.0000]),
              'viral load distribution on ART': np.array([0.0003, 0.0036, 0.0217, 0.0963, 0.3787, 0.4994, 0.0000, 0.0000]),
              'rio': {'viral load distribution': np.array([0.1141, 0.0554, 0.0580, 0.1027, 0.2987, 0.3709, 0.0000, 0.0000]),
                      'incidence': np.array([4.3, 1]),
                      'index positive': 16999,
                      'index negative': 94104,
                      'on ART': 0.73
                      },
              'salvador': {'viral load distribution': np.array([0.1226, 0.0593, 0.0607, 0.1032, 0.2928, 0.3614, 0.0000, 0.0000]),
                      'incidence': np.array([2.45, 1]),
                      'index positive': 3926,
                      'index negative': 41728,
                      'on ART': 0.71
                      },
              'manaus': {'viral load distribution': np.array([0.1268, 0.0612	, 0.0621, 0.1034, 0.2898, 0.3566, 0.0000, 0.0000]),
                      'incidence': np.array([1.4, 1]),
                      'index positive': 2828,
                      'index negative': 45937,
                      'on ART': 0.70
                      }
              }

# we want to solve set of linear equations i.e. AX=b
# for that we need matrix A and b
n_of_eq = len(parameters['attia']) - 1 # we are excluding acute state here
A_mat = pd.DataFrame(0, index = np.arange(n_of_eq), columns = np.arange(n_of_eq))
b_vec = pd.DataFrame(0, index = np.arange(n_of_eq), columns = [0, 1])

# calculate community viral load
on_treat = 1
com_vl = np.add(np.multiply(parameters['viral load distribution on ART'][:-1], on_treat), np.multiply(parameters['viral load distribution off ART'][:-1], (1- on_treat)))
attia = parameters['attia'][:-1]

# attia rate ratios
solution = {}
for city in ['rio', 'salvador', 'manaus']:
    for i in range(0, n_of_eq):
        float_vec = np.zeros(n_of_eq)
        if i == 0:
            A_mat.loc[i, :] = com_vl
            b_vec.loc[i, :] = np.multiply(parameters[city]['incidence'], np.divide(parameters[city]['index negative'], parameters[city]['index positive']))
        elif i == n_of_eq - 1:
            A_mat.loc[i, i] = 1
        else:
            float_vec[i-1] = 1
            float_vec[i] = -1 * np.divide(attia[i-1], attia[i])
            A_mat.loc[i, :] = float_vec
            b_vec.loc[i] = 0
    
    # now we have matrix A and b, let's get the solution now
    solution[city] = [sp.linalg.solve(A_mat.values, b_vec.iloc[:, 0].values), sp.linalg.solve(A_mat.values, b_vec.iloc[:, 1].values)]
    