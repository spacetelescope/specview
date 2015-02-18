
# this should be replaced by introspection from the
# astropy.modeling.Model registry. For now, we directly
# store hard-coded instances.

import astropy.modeling.functional_models as models

registry = {
    'Beta1D':               models.Beta1D(1.0, 0.0, 0.0, 0.0),
    'Box1D' :               models.Box1D(1.0, 1.0, 1.0),
    'Const1D':              models.Const1D(0.0),
    'Gaussian1D':           models.Gaussian1D(1.0, 1.0, 1.0),
    'GaussianAbsorption1D': models.GaussianAbsorption1D(1.0, 1.0, 1.0),
    'Linear1D':             models.Linear1D(1.0, 0.0),
    'Lorentz1D':            models.Lorentz1D(1.0, 1.0, 1.0),
    'MexicanHat1D':         models.MexicanHat1D(1.0, 1.0, 1.0),
    'Redshift':             models.Redshift(0.0),
    'Scale':                models.Scale(1.0),
    'Shift':                models.Shift(0.0),
    'Trapezoid1D':          models.Trapezoid1D(1.0, 1.0, 1.0, 0.0)
}


def getComponentName(function):
    name = str(function.__class__)
    return name.split(".")[-1][:-2]

