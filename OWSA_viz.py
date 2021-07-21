#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 17 18:59:52 2020

@author: vijetadeshpande
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import numpy as np
import sys
import link_to_cepac_in_and_out_files as link
import cluster_operations as c_op
import TextFileOperations as t_op

#%%

def yearly_prob(prob_m):
    rate_m = -1 * np.log(1 - prob_m)
    rate_y = 12 * rate_m
    prob_y = 1 - np.exp(-1 * rate_y)
    
    return prob_y


#%% fixed variables

# user input
HORIZON = 60
COHORT = 20000000
SUS_SIZE = 94104 #{'r': 94104, 's': 41728, 'm': 45937}
TOTAL_VARVAL = 4
base =  r'/Users/vijetadeshpande/Downloads/MPEC/Brazil/Rio/1-way SA_R10'
#r'/Users/vijetadeshpande/Downloads/MPEC/Brazil/Salvador/1-way SA_S10' ##r'/Users/vijetadeshpande/Downloads/MPEC/Brazil/Rio/Try this'
var_list = ['PrEPAdherence']#['PrEPAdherence', 'HIVtestFreqInterval', 'PrEPDroputPostThreshold', 'InitAge'] #['HIVtestFreqInterval'] ['PrEPCoverage']# ['PrEPDuration'] #
var_name = {'PrEPAdherence': 'Adherence (%)',
            'HIVtestFreqInterval': 'Tests (per year)',
            'PrEPDroputPostThreshold': 'Dropout (%)',
            'InitAge': 'Mean age of cohort (years)',
            'PrEPCoverage': 'PrEP uptake (%)',
            'PrEPDuration': 'Time to max. uptake (months)',
            'DynamicTransmissionPropHRGAttrib': 'Proportion of HR to HR transmissions'
            }
strategies = ['30 in 36 months']#['30 in 36 months', '30 in 48 months', '40 in 36 months', '40 in 48 months']

# initiate space to save results
plot_df = pd.DataFrame(0, index = np.arange(len(var_list)*len(strategies)*TOTAL_VARVAL), 
                       columns = ['x', 'Variable (x)', 'Averted infections', 'Averted infections (%)', 'PrEP uptake (%)'])

plot_df1 = pd.DataFrame(0, index = np.arange(TOTAL_VARVAL*TOTAL_VARVAL*len(strategies)), 
                        columns = ['PrEP uptake (%)', 'Adherence (%)', 'Dropout (%)', 'Tests (per year)', 'Averted infections (%)'])
idx = -1
for strategy in strategies:
    print(strategy)

    #
    basepath = os.path.join(base, strategy)
    sqpath = os.path.join(base, 'Common runs')
    sqlist = os.listdir(sqpath)
    readbase = os.path.join(basepath, 'Final runs')
    writebase = os.path.join(base, 'Results')
    
    readpaths = {}
    finalpaths = {}
    for var in var_list:
        float_name = 'Final runs for var = %s'%(var)
        readpaths[var] = os.path.join(readbase, float_name)
        finalpaths[var] = os.path.join(writebase, 'Results for var = %s'%(var))
        
    #%%
    
    for var in readpaths:
        
        # check if sq has mutiple files
        multisq = False
        if 'SQ_'+var in sqlist:
            multisq = True
        
        # collect intervention output
        try:
            c_op.collect_output(readpaths[var])
        except:
            pass
        
        # collect SQ output
        if multisq:
            try:
                c_op.collect_output(os.path.join(sqpath, 'SQ_'+var))
            except:
                pass
        
        # read outputs
        # INT
        floatpath = os.path.join(readpaths[var], 'results')
        cepac_outputs = link.import_all_cepac_out_files(floatpath, module = 'regression')
        
        # SQ
        if multisq:
            cepac_outputs['status quo'] = link.import_all_cepac_out_files(os.path.join(sqpath, 'SQ_'+var, 'results'), module = 'regression')
        else:
            cepac_outputs['status quo'] = link.import_all_cepac_out_files(os.path.join(sqpath, 'SQ', 'results'), module = 'regression')['SQ']
            
        # iterate over each file
        for file in cepac_outputs:
            if file == 'status quo':
                continue
            
            # update index
            idx += 1 
            
            # calculate averted infections
            if multisq:
                substring = file.split('=')#file[19:26] + file[30:]
                substring = substring[1][:-4] + '=' + substring[2]
                averted_inf = (cepac_outputs['status quo']['SQ_'+substring]['infections'] - cepac_outputs[file]['infections'])[0:HORIZON].sum()
                averted_tx = (cepac_outputs['status quo']['SQ_'+substring]['transmissions'] - cepac_outputs[file]['transmissions'])[0:HORIZON].sum()
            else:
                averted_inf = (cepac_outputs['status quo']['infections'] - cepac_outputs[file]['infections'])[0:HORIZON].sum()
                averted_tx = (cepac_outputs['status quo']['transmissions'] - cepac_outputs[file]['transmissions'])[0:HORIZON].sum()
            percent_averted_inf = averted_inf / cepac_outputs[file]['infections'][0:HORIZON].sum()
            percent_averted_tx = averted_tx / cepac_outputs[file]['transmissions'][0:HORIZON].sum()
            
            # other values
            x = float(file.split('=')[2])
            
            #
            plot_df.loc[idx, 'Variable (x)'] = var
            plot_df.loc[idx, 'Averted infections'] = SUS_SIZE * (averted_inf/COHORT)
            plot_df.loc[idx, 'Averted infections (%)'] = int(100 * percent_averted_inf)
            plot_df.loc[idx, 'PrEP uptake (%)'] = int(strategy[0:3])
            plot_df.loc[idx, 'Uptake time (months)'] = int(strategy[6:8])
            
            #
            plot_df1.loc[idx, 'PrEP uptake (%)'] = int(strategy[0:3])
            plot_df1.loc[idx, 'Uptake time (months)'] = int(strategy[6:8])
            plot_df1.loc[idx, 'Averted infections (%)'] = float(100 * percent_averted_inf)
            #plot_df1.loc[idx1, 'T max. uptake (m)'] = float(strategy[-2:])
            if var == 'HIVtestFreqInterval':
                plot_df.loc[idx, 'x'] = int(x)
                plot_df1.loc[idx, var_name[var]] = int(x)
                plot_df1.loc[idx, 'Adherence (%)'] = int(74)
                plot_df1.loc[idx, 'Dropout (%)'] = int(0)
                
            elif var == 'PrEPAdherence':
                plot_df.loc[idx, 'x'] = 100 * x #int(100 * x)
                plot_df1.loc[idx, var_name[var]] = int(100 * x)
                plot_df1.loc[idx, 'Dropout (%)'] = int(0)
                plot_df1.loc[idx, 'Tests (per year)'] = int(4)
                
            elif var == 'PrEPDroputPostThreshold':
                plot_df.loc[idx, 'x'] = 100 * yearly_prob(x) #int(100 * yearly_prob(x))
                plot_df1.loc[idx, var_name[var]] = float(100 * x)
                plot_df1.loc[idx, 'Tests (per year)'] = int(4)
                plot_df1.loc[idx, 'Adherence (%)'] = int(74)
                
            elif var == 'InitAge':
                plot_df.loc[idx, 'x'] = int(x/12)
                plot_df1.loc[idx, var_name[var]] = int(x/12)
                plot_df1.loc[idx, 'Tests (per year)'] = int(4)
                plot_df1.loc[idx, 'Adherence (%)'] = int(74)
                plot_df1.loc[idx, 'Dropout (%)'] = int(0)
            
            elif var == 'PrEPCoverage':
                plot_df.loc[idx, 'x'] = int(100 * x)
            
            elif var == 'PrEPDuration':
                plot_df.loc[idx, 'x'] = int(x)
                
            elif var == 'DynamicTransmissionPropHRGAttrib':
                plot_df.loc[idx, 'x'] = x
                plot_df1.loc[idx, var_name[var]] = x
            
        
#
if not os.path.exists(writebase): os.makedirs(writebase)
# set plot encironment
sns.set_style("darkgrid", {"axes.facecolor": ".9"})
sns.set_context("notebook", rc={"lines.linewidth": 1.5}, font_scale = 1.2)
aspect_r = 2
line_alpha = 0.9

# try plotting just one plot 
plot_df = plot_df.replace('PrEPAdherence', 'PrEP adherence (%)')
plot_df = plot_df.replace('HIVtestFreqInterval', 'Test interval (months)')
plot_df = plot_df.replace('PrEPDroputPostThreshold', 'PrEP dropout (%)')
plot_df['PrEP uptake (%)'] = pd.Series(plot_df['PrEP uptake (%)'], dtype = 'category')
plot_df = plot_df.loc[plot_df.loc[:, 'x'] != 900, :]


for z in ['Averted infections', 'Averted infections (%)']:
    # compare all variables at one time
    plt.figure()
    g = sns.FacetGrid(data = plot_df, 
                     row = 'Variable (x)',
                     sharex = False,
                     sharey = True,
                     aspect = aspect_r)#, hue="Coverage time")#, col_wrap=3)
    g = (g.map(sns.lineplot, 
               'x', 
               z,
               'PrEP uptake (%)',
               alpha = line_alpha,
               ci = None).add_legend())#, "WellID")
    
    # title
    #plt.subplots_adjust(top=0.9)
    #g.fig.suptitle('One way sensitivity analysis')
    
    # save
    filename = os.path.join(writebase, 'OWSA results z = %s, horizon = %d years'%(z, int(HORIZON/12)))
    plt.savefig(filename, dpi = 720)

# compare one variable at one time
for variable in ['PrEP adherence (%)', 'Test interval (months)', 'PrEP dropout (%)']:
    float_df = plot_df.loc[plot_df.loc[:, 'Variable (x)'] == variable, :]
    plt.figure()
    g = sns.FacetGrid(data = float_df, 
                     row = 'Uptake time (months)',
                     col = 'PrEP uptake (%)',
                     sharex = True,
                     sharey = False,
                     aspect = aspect_r)#, hue="Coverage time")#, col_wrap=3)
    g = (g.map(sns.lineplot, 
               'x', 
               'Averted infections',
               alpha = line_alpha,
               ci = None).add_legend())#, "WellID")
    
    # title
    #plt.subplots_adjust(top=0.9)
    #g.fig.suptitle('One way sensitivity analysis')
    
    # save
    filename = os.path.join(writebase, 'OWSA on var = %s, horizon = %d years'%(variable, int(HORIZON/12)))
    plt.savefig(filename, dpi = 720)



"""

plt.figure()
pd.plotting.parallel_coordinates(frame = plot_df1, class_column = 'Averted infections (%)')


plt.figure()
import plotly.express as px
df = px.data.iris()
fig = px.parallel_coordinates(plot_df1, color = 'Averted infections (%)',
                              dimensions=["PrEP uptake (%)", 
                                          "Adherence (%)", 
                                          "Dropout (%)",
                                          "Tests (per year)"],
                              labels={"PrEP uptake (%)": "PrEP uptake",
                                      "Adherence (%)": "Adherence", 
                                      "Dropout (%)": "Dropout",
                                      "Tests (per year)": "Tests", },
                             color_continuous_scale=px.colors.diverging.Tealrose,
                             color_continuous_midpoint=2)
#fig.show()
filename = os.path.join(writebase, 'par plot')
plt.savefig(filename, dpi = 720)



#
def parallel_coordinates(frame, class_column, cols=None, ax=None, color=None,
                     use_columns=False, xticks=None, colormap=None,
                     **kwds):
    import matplotlib.pyplot as plt
    import matplotlib as mpl

    n = len(frame)
    class_col = frame[class_column]
    class_min = np.amin(class_col)
    class_max = np.amax(class_col)

    if cols is None:
        df = frame.drop(class_column, axis=1)
    else:
        df = frame[cols]

    used_legends = set([])

    ncols = len(df.columns)

    # determine values to use for xticks
    if use_columns is True:
        if not np.all(np.isreal(list(df.columns))):
            raise ValueError('Columns must be numeric to be used as xticks')
        x = df.columns
    elif xticks is not None:
        if not np.all(np.isreal(xticks)):
            raise ValueError('xticks specified must be numeric')
        elif len(xticks) != ncols:
            raise ValueError('Length of xticks must match number of columns')
        x = xticks
    else:
        x = range(ncols)

    fig = plt.figure()
    ax = plt.gca()

    Colorm = plt.get_cmap(colormap)

    for i in range(n):
        y = df.iloc[i].values
        kls = class_col.iat[i]
        ax.plot(x, y, color=Colorm((kls - class_min)/(class_max-class_min)), **kwds)

    for i in x:
        ax.axvline(i, linewidth=1, color='black')

    ax.set_xticks(x)
    ax.set_xticklabels(df.columns)
    ax.set_xlim(x[0], x[-1])
    ax.legend(loc='upper right')
    ax.grid()

    bounds = np.linspace(class_min,class_max,10)
    cax,_ = mpl.colorbar.make_axes(ax)
    cb = mpl.colorbar.ColorbarBase(cax, cmap=Colorm, spacing='proportional', ticks=bounds, boundaries=bounds, format='%.2f')

    return fig


plt.figure()
fig = parallel_coordinates(plot_df1, 'Averted infections (%)')
plt.savefig('xyz')




people = var_list
num_people = len(people)
time_spent = np.random.uniform(low=5, high=100, size=num_people)
proficiency = np.abs(time_spent / 12. + np.random.normal(size=num_people))
pos = np.arange(num_people) + .5 # bars centered on the y axis
fig, (ax_left, ax_right) = plt.subplots(ncols=2)
ax_left.barh(pos, time_spent, align='center', facecolor='cornflowerblue')
ax_left.set_yticks([])
ax_left.set_xlabel('Hours spent')
ax_left.invert_xaxis()
ax_right.barh(pos, proficiency, align='center', facecolor='lemonchiffon')
ax_right.set_yticks(pos)
ax_right.set_yticklabels(people, ha='center', x=-0.08)
ax_right.set_xlabel('Proficiency')
plt.suptitle('Learning Python')
plt.show()
"""