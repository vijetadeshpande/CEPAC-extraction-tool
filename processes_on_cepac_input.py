# -*- coding: utf-8 -*-
"""
Created on Wed Jul  3 15:03:28 2019

@author: Vijeta
"""

import pandas as pd
import numpy as np
import glob
import os
from copy import deepcopy
import link_to_cepac_in_and_out_files as link
import dynamic_transmissions_module as dtm


class CepacInput:

    # %%
    def __init__(self, path, sensitivity_module = False, transmission_module = False):
        
        # get independent variable names and values
        self.independent_var, self.independent_var_val = link.extract_ind_var_and_val(path)
        
        # perform either sensitivity module or transmission module
        if sensitivity_module:
            # read perturbation file
            self.perturbation = link.import_perturbation_file(os.path.join(path, r'Input files'))
                
            for folder in os.listdir(os.path.join(path, r'Input files')):
                # read the input data for base-case, intervention and perturbation. Point it to correct attribute
                # make input_files folder as current directory
                self.base_files = link.import_all_cepac_in_files(os.path.join(path, r'Input files', folder))
                # following attribute will be 'True' if all the files for sensitivity analysis have been created
                self.sensitivity_files = self.get_sensitivity_analysis_files(os.path.join(path, r'Input files', folder))
            
        elif transmission_module:
            # run the transmission module
            self.transmission_rate_multiplier = dtm.initialize_tx_module(path)
            # replace the values of m_bar_tx and write the files
            
        else:
            print('You have not activated any module among sensitivity and transmissions')
            
    # %% supportive function for writing all in-files for sensitivity analysis

    def write_files(self, dim1,
                    intervention_file,
                    index_of_current_var,
                    path,
                    index_value_in_perturbation,
                    variable_under_consideration,
                    variable_values_sheet_perturbation):

        # in this case there will be an array of replace_index
        # and we have to find out which row to select for
        # replacing data
        if len(index_of_current_var) > 1:
            index_of_current_var = intervention_file.iloc[index_of_current_var, :].loc[
                                   intervention_file[1] == dim1.values[0], :].index.values

        replace_col = intervention_file.iloc[index_of_current_var, :].dropna(axis=1).columns[
                      2 - int(dim1.empty):].values

        # using var_sheet replace the row-col (replace_index-replace_col)
        # with values mentioned in the perturbation file,
        # one by one

        # create a folder with name of current var
        new_path = path + r'\/' + str(index_value_in_perturbation) + '. ' + variable_under_consideration
        if not os.path.exists(new_path):
            os.makedirs(new_path)

        # iterate over the values mentioned in perturbation file 
        # for sensitivity analysis
        for i in variable_values_sheet_perturbation.index:
            # copy main intervention file
            intervention_float = deepcopy(intervention_file)
            
            # replace values with perturbation values
            intervention_float = self.check_dependancies_and_replace()
            
            #%% it'll be better we create a central function for replacing values.
            # whenever you have to changeany value in .in file, you have to call 
            # that function.
            # Most importantly, function should take care of the dependancies 
            # between different variables 
            
            ##################################################################
            
            if variable_under_consideration in self.independant_var:
                val = {'x_cepac': {}, 'x_user_in': {}}
                val['x_user_in'][variable_under_consideration] = variable_values_sheet_perturbation.iloc[i,2:].values
                if variable_under_consideration == 'percenatge_reduction':
                    intervention_float = link.calculations_for_depemdent_var(intervention_float, self.dependent_var_map[0], val)
                elif variable_under_consideration == 'prep_efficacy':
                    print('\n\n================================================')
                    val['x_user_in']['prep_adherence'] = input('\nPlease enter PrEP adherence value for basecase: \n')
                    intervention_float = link.calculations_for_depemdent_var(intervention_float, self.dependent_var_map[1], val)
                elif variable_under_consideration == 'prep_adherence':
                    print('\n\n================================================')
                    val['x_user_in']['prep_eficacy'] = input('\nPlease enter PrEP efficacy value for basecase: \n')
                    intervention_float = link.calculations_for_depemdent_var(intervention_float, self.dependent_var_map[1], val)
            else:
                intervention_float.iloc[index_of_current_var, replace_col] = variable_values_sheet_perturbation.iloc[i,
                                                                         2:].values
            
            #%%
            
            # save the file
            save_path = new_path + r'\/' + str(variable_under_consideration) + r' value ' + str(i + 1) + r'.in'
            link.write_cepac_in_file(save_path, intervention_float)

    # %%
    def get_sensitivity_analysis_files(self, path):

        # create a new folder which can directly be uploaded on cluster
        run_folder_name = r'Runs prepared for sensitivity analysis'
        if not os.path.exists(os.path.join(path, run_folder_name)):
            os.makedirs(os.path.join(path, run_folder_name))
            path = os.path.join(path, run_folder_name)
        else:
            path = os.path.join(path, run_folder_name)
        
        # define a number to replace na in df
        end_string = 'stop'

        # get input data i.e. cepac input for the intervention scenario
        for i in self.base_files:
            if 'intervention' in i:
                intervention = deepcopy(self.base_files[i])
                break
            elif 'RunB' in i:
                intervention = deepcopy(self.base_files[i])

        # variable perturbation
        perturbation = deepcopy(self.perturbation)
        perturbation['Variable names'] = perturbation['Variable names'].fillna(end_string)

        # create structured perturbation data
        row_index = -1
        for var in perturbation['Variable names']['variable name']:

            # update row index
            row_index += 1
            if var == perturbation['Variable names']['variable name'][0]:
                continue

            # break the loop when there's no variable left to do S.A. over
            if var == end_string:
                break

            # get the values of for S.A. for respective variable
            var_float = perturbation['Variable names']['float name'][row_index]
            var_sheet = perturbation[var_float].iloc[2:, :].reset_index(drop = True)
            var_sheet = var_sheet.iloc[var_sheet[1].first_valid_index():var_sheet[1].last_valid_index() + 1, :].dropna(
                axis=1)
            
            #%% if variable under consideration is efficacy or adherance, you
            # won't find in .in file
            
            ##################################################################
            # find index of current variable in the CEPAC input file 
            replace_index = intervention.index[intervention[0] == var]
            
            #%%

            # check if there are multiple rows for current variable
            if len(replace_index) != 1:

                # select the specific dimension for S.A.

                # take dimension value from perturbation
                dim1 = perturbation['Variable names']['dim1'].loc[
                    perturbation['Variable names'].loc[:, 'variable name'] == var]

                # if that dimension is not availble in CEPAC_input the thre's 
                # something wrong
                if dim1.values[0] not in intervention.loc[replace_index, 1].values[:]:

                    print('Error')

                # if that specific value is available in CEPAC_input then see 
                # if there's any dim2 mentioned in the perturbation file
                else:

                    dim2 = perturbation['Variable names']['dim2'].loc[
                        perturbation['Variable names'].loc[:, 'variable name'] == var]

                    # %%
                    # if there's no second dimention mentioned then we'll 
                    # replace the entire array of inputs corresponding to dim1
                    if dim2.values[0] == end_string:

                        # write the file
                        self.write_files(dim1=dim1,
                                         intervention_file=intervention,
                                         index_of_current_var=replace_index,
                                         path=path,
                                         index_value_in_perturbation=row_index,
                                         variable_under_consideration=var,
                                         variable_values_sheet_perturbation=var_sheet)


                    # %%
                    # if there's a second dimension mentioned in the perturbation 
                    # file then we'll replace only one value in the array
                    # of inputs corresponding to dim1
                    else:

                        # if that dimension is not available in CEPAC_input the thre's
                        # something wrong
                        if dim2.values[0] not in intervention.loc[replace_index, 1].values[:]:

                            # this section is not written correctly
                            print('Error')

                        # if that specific value is available in CEPAC_input then see 
                        # if there's any dim2 mentioned in the perturbation file
                        else:

                            # this section is not written correctly
                            print('Error')

            # %%
            # if there's only one element in replace_index 
            else:

                # write the file
                self.write_files(dim1=pd.DataFrame(),
                                 intervention_file=intervention,
                                 index_of_current_var=replace_index,
                                 path=path,
                                 index_value_in_perturbation=row_index,
                                 variable_under_consideration=var,
                                 variable_values_sheet_perturbation=var_sheet)
                
        # shift files for basecase and intervention to a folder
        data = self.basecase_intervention
        new_path = os.path.join(path, r'Basecase and Intervention')
        if not os.path.exists(new_path):
            os.makedirs(new_path)
        for file in data:
            link.write_cepac_in_file(os.path.join(new_path, file+r'.in'), data[file])
            #os.remove(os.path.join(path, file+r'.in'))

        return True
    
    def check_dependancies_and_replace(self, var):
        
        # check if the variable
        
        return


'''

sample = a['perturbation.xlsx']['Variable names']

'''
