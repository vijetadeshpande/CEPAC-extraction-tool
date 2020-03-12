# -*- coding: utf-8 -*-
"""
Created on Thu Jul 25 10:08:26 2019

@author: Vijeta
"""
from ProjectDetails import ProjectDetails
from processes_on_cepac_output import CepacOutput
from processes_on_cepac_output import get_comparative_results
import os
from sys import getsizeof
import visualization as viz


# get current path
tool_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..'))

# saving path names for respective folders
path_names = {'sensitivity': os.path.join(parent_dir, 'Sensitivity runs'),
              'transmission': os.path.join(parent_dir, 'Transmission runs')}

# create a project object and treat it as a root node
brazil_prep = ProjectDetails(title="brazil prep", aim="CEA of prep for MSM", country="Brazil")

# read all the cepac outputs
cepac_results = CepacOutput(path_names, sensitivity_module = True).output_data

# plotting outputs
#for var in output_objects:
popstat_dict = {}
  
# send it to visualization
comparative_results = get_comparative_results(popstat_dict)

