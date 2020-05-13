#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 27 17:11:50 2020

@author: vijetadeshpande
"""

import numpy as np
import pandas as pd
from copy import deepcopy
import os
import scipy.optimize as opt

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
              
# function for calculating error
def expand_acute(acute_rate):
    new_rates = []
    for i in parameters['attia']:
        k = np.multiply(0.017311, np.divide(i, parameters['attia'][-1]))
        new_rates.append(np.multiply(acute_rate, k))
    
    return new_rates
    
def predict(on_treat, acute_rate):
    # calculate other transmission rates
    new_rates = expand_acute(acute_rate)
    
    # calculate distribution
    dist = np.multiply(on_treat, parameters['viral load distribution on ART']) + np.multiply((1 - on_treat), parameters['viral load distribution off ART'])
    y_hat = np.array([np.sum(np.multiply(new_rates, dist))])
    
    return y_hat

def predict2(on_treat):
    dist = np.multiply(on_treat, parameters['viral load distribution on ART']) + np.multiply((1 - on_treat), parameters['viral load distribution off ART'])
    attia = np.multiply(7.79, parameters['attia'])
    y_hat = np.array([np.sum(np.multiply(attia, dist))])
    y = np.multiply(parameters[city]['incidence'][0], np.divide(parameters[city]['index negative'], parameters[city]['index positive']))
    residual = np.power((y_hat - y), 2)
    
    return residual
    
# treatment
treat = [0.73] #[0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]
solution_lib = {}
for city in ['rio', 'salvador', 'manaus']:
    solution_lib[city] = {}
    for t in treat:
        solution_acute = opt.curve_fit(f = predict, 
                                   xdata = t,
                                   ydata = np.multiply(parameters[city]['incidence'][0], np.divide(parameters[city]['index negative'], parameters[city]['index positive'])),
                                   p0 = 62.56,
                                   method = 'lm')
        
        # store value
        solution_lib[city][t] = expand_acute(solution_acute[0][0])

#
solution_lib1 = {}
for city in ['rio', 'salvador', 'manaus']:
    sol = opt.least_squares(fun = predict2, 
                            x0 = 1,
                            method = 'lm')
    solution_lib1[city] = sol['x'][0]
