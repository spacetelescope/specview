from astropy.modeling import fitting
import numpy as np

from specview.tools import model_io as mio

fitter = fitting.LevMarLSQFitter()
x = np.array([100.,400.,800.,1200.,1500.,1800.,2100.,2400.])
y = np.array([0.,50.,200.,400.,300.,200.,100.,10.])

compound_model, directory = mio.buildModelFromFile("/Users/busko/atest6.py")
print(compound_model)

result = fitter(compound_model, x, y)
print(result)

compound_model, directory = mio.buildModelFromFile("/Users/busko/atest6.py")
print(compound_model)
