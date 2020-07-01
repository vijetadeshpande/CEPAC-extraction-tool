#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May  5 12:05:40 2020

@author: vijetadeshpande
"""

import scipy as sp
import scipy.optimize
import numpy as np

#%% aux functions
def normal_to_log(mean, sd):
    log_sd = np.power(np.log(1 + np.divide(np.power(sd, 2),np.power(mean, 2))), 0.5)
    log_mean = np.log(mean) - np.divide(np.power(log_sd, 2), 2)

    return log_mean, log_sd

def gauss(x, a, b, c):
    return np.multiply(a, np.exp(-1 * np.divide(np.power((x-b), 2), np.power(2*c, 2))))

def rate_to_prob(x, factor = 1):
    x = np.divide(x, factor)
    prob = 1 - np.exp(-1 * x)
    
    return prob
#%% inputs
size = 5000000
normal_sd = 9.6
normal_mean = 30
log_mean, log_sd = normal_to_log(normal_mean, normal_sd)

# simulate
samples = []
for sample in range(0, size):
    
    # 
    x = log_mean + np.multiply(log_sd, np.random.normal(loc = 0, scale = 1, size = 1))
    y = np.exp(x)
    if y > 16 and y < 100:
        samples.append(y[0])

#
counts, bin_edges = np.histogram(samples, bins = [16, 18, 25, 30, 40, 46, 51, 55, 100])
prob = np.divide(counts, size)

#
#counts, bin_edges = np.histogram(samples, bins = [16, 20, 26, 31, 36, 41, 45, 100])
#prob = np.divide(counts, size)

#
if True:
    x_d = np.array([16, 18, 25, 30, 40, 46, 51, 55])
    y_d = np.array([4.3, 4.3, 4.3, 4.3, 1, 1, 1, 1])
    #np.array([2.45, 2.45, 2.45, 2.45, 0.5698, 0.5698, 0.5698, 0.5698]) 
    #np.array([4.3, 4.3, 4.3, 4.3, 1, 1, 1, 1])
    #np.array([1.4, 1.4, 1.4, 1.4, 0.3256, 0.3256, 0.3256, 0.3256])
    solution = sp.optimize.curve_fit(gauss, x_d, y_d, p0 = [1, normal_mean, normal_sd])
    opt_a, opt_b, opt_c = solution[0][0], solution[0][1], solution[0][2]
    y_hat = gauss(x_d, opt_a, opt_b, opt_c)
    y_hat_prob = rate_to_prob(y_hat, 1200)
