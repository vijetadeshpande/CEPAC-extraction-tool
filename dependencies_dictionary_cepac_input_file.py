# -*- coding: utf-8 -*-
"""
Created on Thu Oct 31 11:37:52 2019

@author: Vijeta
"""

list_of_dependent_var = ["DynamicTransmissionNumTransmissionsHRG", "PrepIncidMale",\
                         "PrepIncidFemale", "HIVIncidReductionCoefficient"]

dependencies = {}

dependencies["DynamicTransmissionNumTransmissionsHRG"] = {\
            'in_ind': ["TransmissionRateOnART", "TransmissionRateOnART"],\
            "in_dep": [],\
            "excel_ind": [r"VL Distribution of HRG population in index year"]}

dependencies["PrepIncidMale"] = {\
            'in_ind': ["HIVmthIncidMale"],\
            "in_dep": [],\
            "excel_ind": [r"PrEP Efficacy", r"PrEP Adherence"]}

dependencies["PrepIncidFemale"] = {\
            'in_ind': ["HIVmthIncidFemale"],\
            "in_dep": [],\
            "excel_ind": [r"PrEP Efficacy", r"PrEP Adherence"]}

dependencies["HIVIncidReductionCoefficient"] = {\
            'in_ind': ["HIVIncidReductionStopTime"],\
            "in_dep": [],\
            "excel_ind": [r"Total Proportion HIV Incidence Reduction"]}

#%%
U = []
for k in dependencies:
    for type_v in dependencies[k]:
        U = U | dependencies[k]

#%%
def check_dependency(var):
    
    if var in U:
        return dependencies[var]
    else:
        return {}