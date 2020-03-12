__author__ = 'Vijeta Deshpande'

from CepacOutput import CepacOutput
from ProjectDetails import ProjectDetails


# create a project object and treat it as a root node
brazil_prep = ProjectDetails(title="brazil prep", aim="CEA of prep for MSM", country="Brazil")

# saving path names for respective folders
path_names = {'input': r'C:\Users\Vijeta\Documents\Projects\Brazil PrEP\Sensitivity analysis\Input files',
              'output': r''}

# creating input data node
brazil_prep.database = CepacOutput(path_names, brazil_prep)









