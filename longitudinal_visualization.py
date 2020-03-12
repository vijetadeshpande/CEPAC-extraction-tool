# -*- coding: utf-8 -*-
"""
Created on Tue Nov 12 11:57:36 2019

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

path = {'Output': r'C:\Users\Vijeta\Documents\Projects\Brazil PrEP\Transmission runs\Input files\Runs prepared for calculating percentage decline in incidence\Brazil\results'}

# get output data
"""
long_out_dict = link.import_all_cepac_out_files(path['Output'], extensions = [r'\*.txt'])

def fill_empty_val(a, df):
    
    empty_val = -1
    if len(a) == 0:
        return empty_val
    else:
        return df.loc[a[0], 0][2:]

# let's try to plot three transitions (to acute, to chronic and to death)
long_data_dict = {}
for run in long_out_dict:
    pat_death = long_out_dict[run]["death transmissions"].reset_index()
    long_df = pd.DataFrame(-1, columns = ["Start gender", "Start age", "Start HIV state", "Start CHRMS state", "Start PrEP state", "To acute HIV", "To chronic HIV", "To death", "Death reason"], index = np.arange(0, len(long_out_dict[run]) - 1))
    for pat in long_out_dict[run]:
        if pat == "death transmissions":
            continue
        
        # first fill all initial condition
        long_df.loc[pat, ["Start gender", "Start age", "Start HIV state", "Start CHRMS state", "Start PrEP state"]] = long_out_dict[run][pat]["starting condition"].values[0]
        
        # enter into the key = trajectory
        pat_cur = long_out_dict[run][pat]["trajectory"]["non death transmissions"]
        to_acute, to_chronic = pat_cur.loc[pat_cur.loc[:, 2] == "INFECTION;", :].index.values, pat_cur.loc[pat_cur.loc[:, 4] == "CHR:", :].index.values
        to_acute, to_chronic = fill_empty_val(to_acute, pat_cur), fill_empty_val(to_chronic, pat_cur)
        to_death, death_reason = pat_death.loc[pat, 0][2:], pat_death.loc[pat, 2][:-1]
        pat_transitions = [to_acute, to_chronic, to_death, death_reason]
        pat_transitions = np.array(pat_transitions, dtype = object)
        long_df.loc[pat, ["To acute HIV", "To chronic HIV", "To death", "Death reason"]] = pat_transitions[:]
    long_data_dict[run] = long_df
"""




#%% plot monte carlo trajectories
sb.set_style("darkgrid", {"axes.facecolor": ".9"})
sb.set_context("notebook", rc={"lines.linewidth": 0.2})

fig = plt.figure()
for run in long_data_dict:
    run_col = (run == 'A') * ("k") + (run == 'B') * ("r") + (run == 'C') * ("c")
    for pat in long_data_dict[run].index:
        x = []
        y = []
        
        # x = age and y = health state, start appending values from start age
        start_age = int(long_data_dict[run].loc[pat, "Start age"])
        x.append(start_age)
        y.append(3)#("Start condition")
        
        # see this sample gets infected
        if long_data_dict[run].loc[pat, "To acute HIV"] != -1:
            # acute
            x.append(int(long_data_dict[run].loc[pat, "To acute HIV"]) + start_age)
            y.append(2)#("Acute HIV")
            # chronic
            x.append(int(long_data_dict[run].loc[pat, "To chronic HIV"]) + start_age)
            y.append(1)#("Chronic HIV")
            # death
            x.append(int(long_data_dict[run].loc[pat, "To death"]) + start_age)
            y.append(0)#("Death")
        else:
            # death
            x.append(int(long_data_dict[run].loc[pat, "To death"]) + start_age)
            y.append(0)#("Death")
        
        # df to plot
        plot_frame = pd.DataFrame(columns = ["Age (months)", "Health state"])
        plot_frame["Age (months)"], plot_frame["Health state"] = x, y
        plot_frame["Age (months)"] = plot_frame["Age (months)"].astype('int32')
        plot_frame["Health state"] = plot_frame["Health state"].astype('category')
        # seaborn plot
        #cur_traj = sb.lineplot(x = 'Age (months)', y = 'Health state', data = plot_frame)#, alpha = 0.2)
        plt.plot(x, y, alpha = 0.01, color = run_col)
        plt.scatter(x, y, alpha = 0.004, color = run_col)

    plt.draw()
    plt.savefig(run + 'sample monte1.png', bbox_inches='tight')#, dpi = 360)
    plt.show()


#%% experiment on parameter estimation

