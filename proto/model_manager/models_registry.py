
# this should (perhaps?) be replaced by introspection from
# the astropy.modeling.Model registry. For now, we directly
# store hard-coded instances.

import astropy.modeling.models as models
from astropy.modeling import Parameter, Fittable1DModel
from astropy.modeling.polynomial import PolynomialModel

registry = {
    'Gaussian1D':                 models.Gaussian1D(1.0, 1.0, 1.0),
    'GaussianAbsorption1D':       models.GaussianAbsorption1D(1.0, 1.0, 1.0),
    'Lorentz1D':                  models.Lorentz1D(1.0, 1.0, 1.0),
    'MexicanHat1D':               models.MexicanHat1D(1.0, 1.0, 1.0),
    'Trapezoid1D':                models.Trapezoid1D(1.0, 1.0, 1.0, 1.0),
    'Moffat1D':                   models.Moffat1D(1.0, 1.0, 1.0, 1.0),
    'ExponentialCutoffPowerLaw1D':models.ExponentialCutoffPowerLaw1D(1.0, 1.0, 1.0, 1.0),
    'BrokenPowerLaw1D':           models.BrokenPowerLaw1D(1.0, 1.0, 1.0, 1.0),
    'LogParabola1D' :             models.LogParabola1D(1.0, 1.0, 1.0, 1.0),
    'PowerLaw1D' :                models.PowerLaw1D(1.0, 1.0, 1.0),
    'Linear1D':                   models.Linear1D(1.0, 0.0),
    'Const1D':                    models.Const1D(0.0),
    'Redshift':                   models.Redshift(0.0),
    'Scale':                      models.Scale(1.0),
    'Shift':                      models.Shift(0.0),
    'Sine1D' :                    models.Sine1D(1.0, 1.0),
    'Chebyshev1D':                models.Chebyshev1D(1),
    'Legendre1D' :                models.Legendre1D(1),
    'Polynomial1D' :              models.Polynomial1D(1),
}

# this nightmarish way of getting the function name results from the way
# astropy functional models store them. Both their '_name' and 'name'
# attributes are set to None, and a plain, easy to use name is nowhere
# to be seen. And worse, the name coding changed  dramatically from
# astropy 0.4 to 1.0.
def getComponentName(function):
    if issubclass(function.__class__, Fittable1DModel):
        name = function.__class__()
        return _getName(name)
    elif issubclass(function.__class__, PolynomialModel):
        name = function.__class__
        return _getName(name)

def _getName(name):
    return str(name).split("Inputs")[0].split(":")[1][1:-1]


