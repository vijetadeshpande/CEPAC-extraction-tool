# -*- coding: utf-8 -*-
"""
Created on Wed Feb 26 13:52:28 2020

@author: Vijeta
"""

import numpy as np

prep_par = {'efficacy': 0.96, 'retention': 0.74, 'Initial population on prep': 0,
            'target uptake': 0.3, 'target uptake time': 36}
population = {'susceptible': 61749, 'prep': 0, 'incident cases': 0}
transition_par = {'birth rate': 0.0067, 'to prep given sus': 0,
                  'to positive given prep': 0, 'to positive given not prep': 0, 
                  'prep retention': 0.74}

#
pop_sus = np.multiply(population['susceptible'], np.power((1 + transition_par['birth rate']), np.divide(np.arange(0,121), 12)))
prob_prep_uptake =  np.zeros(len(pop_sus))
prob_prep_uptake[:prep_par['target uptake time']] = np.divide(prep_par['target uptake'], prep_par['target uptake time'])
prob_prep_uptake = prob_prep_uptake.cumsum()
pop_total_prep_uptake = np.multiply(prob_prep_uptake, pop_sus)

#
prob_prep_dropout = 1 - np.exp(np.divide(np.log(prep_par['retention']), 12))
pop_prep_dropout = np.zeros(len(pop_sus))

#
pop_prep_start = np.zeros(len(pop_sus))
pop_prep_leave = np.zeros(len(pop_sus))
pop_prep_net = np.zeros(len(pop_sus))
pop_no_prep = np.zeros(len(pop_sus))
pop_no_prep[0] = population['susceptible']
pop_hiv_prep = np.zeros(len(pop_sus))
pop_hiv_no_prep = np.zeros(len(pop_sus))
modified_hiv = np.zeros(len(pop_sus))
incident_cases = np.array([0, 74.42322355,	41.31316435,	37.5146704,	42.90478892,	43.30200017,	43.54090234,	44.13561487,	44.50090835,	44.8712812,	45.23123706,	45.60448273,	46.35932759,	47.16971819,	48.32733363,	47.79343123,	48.12807053,	48.42595975,	48.66767053,	48.8349413,	49.0394159,	49.2191263,	49.37970625,	49.51836434,	49.64124494,	49.75648503,	49.86366456,	49.94090682,	50.01651648,	50.08362537	,50.12078252,	50.15962951,	50.19592755,	50.20920137,	50.22537593,	50.23056052,	50.22501114,	50.21827695,	50.23170573,	50.25255273,	50.29444733,	50.33821998,	50.3758998,	50.41000717,	50.4523114,	50.48855027,	50.52952832,	50.57081521,	50.60168272,	50.64675132,	50.69367289,	50.73017958,	50.76856968,	50.81436753,	50.85146354,	50.89325665,	50.93420879,	50.97523893,	51.01645972,	51.05873413,	51.09951886,	51.14456512,	51.19272099,	51.23477839,	51.2770485,	51.32338149,	51.36637387,	51.40917361,	51.46527848,	51.51140705,	51.56287827,	51.61531234,	51.66503466,	51.71868005,	51.7745005,	51.82747197,	51.88261338,	51.93645669,	51.98878863,	52.04048058	,52.09915313,	52.15351088,	52.20729207,	52.26745298,	52.31923031,	52.37569931,	52.43695463,	52.49322903,	52.550776,	52.60985632,	52.66246228	,52.71765438,	52.77499487,	52.82478597,	52.88365289	,52.94201669,	52.99156256,	53.04888799,	53.10865739,	53.16458527,	53.22399047,	53.2904659,	53.34262716,	53.39811239,	53.45684164,	53.51468345,	53.57100376,	53.63216785,	53.68892555,	53.74712962,	53.80556467,	53.85813627,	53.91319838,	53.96845518,	54.01969407,	54.07142493,	54.12539742,	54.1765119,	54.23017537,	54.28036715,	54.33198444])
for i in range(1, len(pop_sus)):
    pop_prep_start[i] = pop_total_prep_uptake[i] - pop_total_prep_uptake[i-1]
    pop_prep_leave[i] = prob_prep_dropout * pop_prep_net[i-1]
    pop_prep_net[i] = pop_prep_net[i-1] + pop_prep_start[i] - pop_hiv_prep[i-1] - pop_prep_leave[i]
    pop_no_prep[i] = pop_no_prep[i-1] - pop_hiv_no_prep[i-1] - pop_prep_start[i] + pop_prep_leave[i] + (pop_sus[i] - pop_sus[i-1])
    f_prep = pop_prep_net[i]/(pop_prep_net[i] + pop_no_prep[i])
    f_no_prep = pop_no_prep[i]/(pop_prep_net[i] + pop_no_prep[i])
    pop_hiv_prep[i] = f_prep * (1 - prep_par['efficacy']) * incident_cases[i]
    pop_hiv_no_prep[i] = f_no_prep * incident_cases[i]
    modified_hiv[i] = pop_hiv_prep[i] + pop_hiv_no_prep[i]