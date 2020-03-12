# -*- coding: utf-8 -*-
"""
Created on Fri Jan 24 14:28:03 2020

@author: Vijeta
"""

import numpy as np
import link_to_cepac_in_and_out_files as link
import os
import pandas as pd
import re
import transmission_algorithm as tx_algo
import matplotlib.pyplot as plt
import seaborn as sb
from copy import deepcopy
import math
#from joblib import Parallel, delayed
import multiprocessing
import abc_auxilliaries as aux


# Plot percentage reduction for strategies
df = plot_df["percentage reduction"]
'''
df["Strategy"] = df.Strategy.str.replace('(', '')
df["Strategy"] = df.Strategy.str.replace(')', '')
df["Strategy"] = df.Strategy.str.replace(',', '')
df["Coverage"] = pd.DataFrame(df.Strategy.str.split(' ',1).tolist(), columns = ['Coverage','Coverage time'])["Coverage"]
df["Coverage time"] = pd.DataFrame(df.Strategy.str.split(' ',1).tolist(), columns = ['Coverage','Coverage time'])["Coverage time"]
df = df.loc[df['Coverage'].isin(['10%', '20%', '30%']), :]
df["Coverage time"] = df["Coverage time"].str.replace(' months', '')
df["Coverage time"] = pd.to_numeric(df['Coverage time'], errors='coerce')
'''
plt.figure(figsize=(20, 10))
df = df.loc[df['Coverage (%)'].isin([10, 20, 30]), :]
g = sb.FacetGrid(df, col="Coverage (%)", aspect = aspect_r)#, hue="Coverage time")#, col_wrap=3)
g = (g.map(sb.lineplot, "Coverage time (months)", r"Percentage reduction in incidence", "Benefit type", alpha = line_alpha).add_legend())#, "WellID")
g.axes[0,0].set_ylabel(r"Reduction in incidence rate (%)")
plt.savefig(os.path.join(save_path, r'Percentage reduction in incidence'), dpi = 360)
del g


if False:
    # plot intersection of community and direct benefit
    df = plot_df["intersection"]
    '''
    df["Strategy"] = df.Strategy.str.replace('(', '')
    df["Strategy"] = df.Strategy.str.replace(')', '')
    df["Strategy"] = df.Strategy.str.replace(',', '')
    df["Coverage"] = pd.DataFrame(df.Strategy.str.split(' ',1).tolist(), columns = ['Coverage','Coverage time'])["Coverage"]
    df["Coverage time"] = pd.DataFrame(df.Strategy.str.split(' ',1).tolist(), columns = ['Coverage','Coverage time'])["Coverage time"]
    df = df.loc[df['Coverage'].isin(['10%', '20%', '30%']), :]
    df["Coverage time"] = df["Coverage time"].str.replace(' months', '')
    df["Coverage time"] = pd.to_numeric(df['Coverage time'], errors='coerce')
    '''
    df = df.loc[df['Coverage (%)'].isin([10, 20, 30]), :]
    plt.figure()
    g = sb.FacetGrid(df, col="Coverage (%)", aspect = aspect_r)#, hue="Coverage time")#, col_wrap=3)
    g = (g.map(sb.lineplot, "Coverage time (months)", "Intersection of benefits (%)", alpha = line_alpha).add_legend())#, "WellID")
    plt.savefig(os.path.join(save_path, r'intersection of benefits'), dpi = 360)
    del g
    
    df = plot_df["intersection"]
    '''
    df["Strategy"] = df.Strategy.str.replace('(', '')
    df["Strategy"] = df.Strategy.str.replace(')', '')
    df["Strategy"] = df.Strategy.str.replace(',', '')
    df["Coverage"] = pd.DataFrame(df.Strategy.str.split(' ',1).tolist(), columns = ['Coverage','Coverage time'])["Coverage"]
    df["Coverage time"] = pd.DataFrame(df.Strategy.str.split(' ',1).tolist(), columns = ['Coverage','Coverage time'])["Coverage time"]
    df = df.loc[df['Coverage'].isin(['10%', '20%', '30%']), :]
    df["Coverage time"] = df["Coverage time"].str.replace(' months', '')
    df["Coverage time"] = pd.to_numeric(df['Coverage time'], errors='coerce')
    '''
    df = df.loc[df['Coverage (%)'].isin([40, 50, 60]), :]
    plt.figure()
    g = sb.FacetGrid(df, col="Coverage (%)", aspect = aspect_r)#, hue="Coverage time")#, col_wrap=3)
    g = (g.map(sb.lineplot, "Coverage time (months)", "Intersection of benefits (%)", alpha = line_alpha).add_legend())#, "WellID")
    plt.savefig(os.path.join(save_path, r'intersection of benefits1'), dpi = 360)
    del g