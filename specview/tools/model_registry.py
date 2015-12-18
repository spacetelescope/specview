#
# astropy spectral models
#
# this file should (perhaps?) be replaced by some form of
# introspection from the astropy.modeling.Model registry.
# For now, we directly store hard-coded instances.

import astropy.modeling.models as models

registry = {
    'Box1D' :                     models.Box1D(1.0, 1.0, 1.0),
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


def get_component_name(function):
    # there must be a better way of getting the class' name......
    class_string = str(function.__class__)
    return class_string.split('\'>')[0].split(".")[-1]


def get_component_path(function):
    class_string = str(function.__class__)
    module_path = class_string.split('\'')[1]
    index = module_path.rfind('.')
    module_path = module_path[:index]
    return module_path


# Helper functions that handle compound models.
# They are defined in here for convenience. They
# might as well be moved to a better place if the
# need ever arises.

def buildSummedCompoundModel(components):
    # build a compound model from a list of components
    if (type(components) != type([])) or len(components) < 1:
        return None
    result = components[0]
    if len(components) > 1:
        for component in components[1:]:
            result += component
    return result


def getComponents(compound_model):
    # build a list of components from a compound model
    if hasattr(compound_model, '_submodels'):
        return compound_model._submodels
    else:
        return [compound_model]


