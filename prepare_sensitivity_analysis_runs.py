# -*- coding: utf-8 -*-
"""
Created on Wed Jul  3 15:03:28 2019

@author: Vijeta
"""

from processes_on_cepac_input import CepacInput
from ProjectDetails import ProjectDetails
import os

# get current path
tool_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..'))

# create a project object and treat it as a root node
brazil_prep = ProjectDetails(title="brazil prep", aim="CEA of prep for MSM", country="Brazil")

# saving path names for respective folders
path_names = {'sensitivity': os.path.join(parent_dir, 'Sensitivity runs'),
              'transmission': os.path.join(parent_dir, 'Transmission runs')}

# check if following set of files exits
req_in = {'perturbation.xlsx'}

# check if directories exits
if os.path.exists(path_names['sensitivity']):
    if os.path.exists(os.path.join(path_names['sensitivity'], r'Input files')):
        if (req_in & set(os.listdir(os.path.join(path_names['sensitivity'], r'Input files')))) == req_in:
            brazil_prep.database = CepacInput(path_names['sensitivity'], brazil_prep, sensitivity_module = True)
        else:
            print('\nThe folder, Input files, is missing one or more of following required files:')
            print(req_in)
    else:
        print('folder, Input files, should exists for this tool to work. Path should be as follows:')
        print(os.path.join(path_names['sensitivity'], r'Input files'))
else:
    print('folder, Sensitivity runs, should exists for this tool to work. Path should be as follows:')
    print(os.path.join(parent_dir, 'Sensitivity runs'))


#%% Test/debug section
#a = brazil_prep.database.basecase_intervention
#c = brazil_prep.database.perturbation

