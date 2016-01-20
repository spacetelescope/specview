from astropy.modeling import fitting
import numpy as np

from specview.tools import model_io as mio
from specview.tools import model_registry as mr

fitter = fitting.LevMarLSQFitter()
x = np.array([100.,400.,800.,1200.,1500.,1800.,2100.,2400.])
y = np.array([0.,50.,200.,400.,300.,200.,100.,10.])

compound_model, directory = mio.buildModelFromFile("/Users/busko/atest6.py")
print("Compound model after first read: ")
print(compound_model)
print("and _submodels after first read look like this: ")
print(mr.getComponents(compound_model))

result = fitter(compound_model, x, y)
print("Fitted results: ")
print(result)

compound_model, directory = mio.buildModelFromFile("/Users/busko/atest6.py")
print("Compound model after second read: ")
print(compound_model)
print("and _submodels after second read look like this: ")
print(mr.getComponents(compound_model))
