
# this should (perhaps?) be replaced by introspection from
# the astropy.modeling.Model registry. For now, we directly
# store hard-coded instances.

# import astropy.modeling.functional_models as models
import astropy.modeling.models as models

registry = {
    'Gaussian1D':                 models.Gaussian1D(1.0, 1.0, 1.0),
    'GaussianAbsorption1D':       models.GaussianAbsorption1D(1.0, 1.0, 1.0),
    'Lorentz1D':                  models.Lorentz1D(1.0, 1.0, 1.0),
    'MexicanHat1D':               models.MexicanHat1D(1.0, 1.0, 1.0),
    'Trapezoid1D':                models.Trapezoid1D(1.0, 1.0, 1.0, 1.0),
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


def getComponentName(function):
    # this nightmarish way of getting the function name results from the way
    # astropy functional models store them. Both their '_name' and 'name'
    # attributes are both set to None. Why???? And worse, the name coding
    # changed dramatically from astropy 0.4 to 1.0. We hope that it either
    # stays stable from now on, or, better, the name attributes get populated
    # by the constructor as they should.
    name = function.__class__()
    return str(name).split("Inputs")[0].split(":")[1][1:-1]

