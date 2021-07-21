#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 22 17:43:58 2020

@author: vijetadeshpande
"""
import numpy as np
import scipy as sp
import scipy.optimize as opt
import pandas as pd


# desired distribution
des_mean = 492
des_sd = 320
des_samples = np.random.normal(loc = des_mean, scale = des_sd, size = 10000)
des_samples_root = np.power(des_samples, 0.5)
init_mean, init_sd = np.mean(des_samples_root), np.std(des_samples_root)

# starting solution (take root of both values)
init_mean = np.power(des_mean, 0.5)
init_sd = np.power(des_sd, 0.5)

# a function calculating mean,sd of actual CD4 values from a transformaed distribution
def get_dist(x_data, sd):

    # desired distribution
    target_mean = 492

    # get 10k samples from the normal distribution
    samples = np.random.normal(loc = np.power(target_mean, 0.5), scale = sd, size = 10000)
    
    # square the values and calculate mean and sd
    CD4_values = np.power(samples, 2)
    sol_mean, sol_sd = np.mean(CD4_values), np.std(CD4_values)
    
    # our solution will be as follows
    solution = np.array([sol_mean])
    
    return solution

# initialize
x = [1]
y = np.array([des_mean])

#
solution = opt.curve_fit(get_dist, x, y, p0 = [init_sd])

    