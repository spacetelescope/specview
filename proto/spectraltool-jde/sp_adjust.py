import numpy as np

import models_registry

# Code in this module is used to "adjust" spectral components
# to the data at hand. This is used by model-fitting code that
# has to create spectral component instances with sensible
# parameter values such that they can be used as first guesses
# by the fitting algorithms.


class _Linear1DAdjuster(object):
    def adjust(self, instance, x, y):

        y_range = np.max(y) - np.min(y)
        x_range = x[len(x) - 1] - x[0]
        slope = y_range / x_range
        y0 = y[0]

        instance.slope.value = slope
        instance.intercept.value = y0

        return instance


class _Const1DAdjuster(object):
    def adjust(self, instance, x, y):
        # is there a better way to define it?
        instance.amplitude.value = 0.0
        return instance


# This class is used to adjust all "line profile" functions
# that basically have an amplitude, a width, and a defined
# position in wavelength space.
class _LineProfile1DAdjuster(object):
    def __init__(self, factor=1.0):
        self._factor = factor

    def adjust(self, instance, x, y):

        y_range = np.max(y) - np.min(y)
        x_range = x[len(x) - 1] - x[0]
        position = x_range / 2.0 + x[0]
        width = x_range / 50.

        name = models_registry.getComponentName(instance)

        _setattr(instance, name, 'amplitude', y_range * self._factor)
        _setattr(instance, name, 'position', position)
        _setattr(instance, name, 'width', width)

        return instance


# Maps parameter names to function type. Prevents a
# non-existent parameter to stop on its tracks
# the parameter value setting sequence.
def _setattr(instance, fname, pname, value):
    try:
        setattr(instance, _p_names[fname][pname], value)
    except KeyError:
        pass


# This associates each adjuster to its corresponding spectral function.
# Some functions are not really line profiles, but their parameter
# names and roles are the same as in a typical line profile, so they
# can be adjusted in the same way.
_adjusters = {
    'Beta1D':                     _LineProfile1DAdjuster(),
    'Box1D':                      _LineProfile1DAdjuster(),
    'Const1D':                    _Const1DAdjuster(),
    'Gaussian1D':                 _LineProfile1DAdjuster(),
    'GaussianAbsorption1D':       _LineProfile1DAdjuster(),
    'Linear1D':                   _Linear1DAdjuster(),
    'Lorentz1D':                  _LineProfile1DAdjuster(),
    'MexicanHat1D':               _LineProfile1DAdjuster(),
    'Trapezoid1D':                _LineProfile1DAdjuster(),
    'PowerLaw1D':                 _LineProfile1DAdjuster(factor=0.5),
    'BrokenPowerLaw1D':           _LineProfile1DAdjuster(factor=0.5),
    'ExponentialCutoffPowerLaw1D':_LineProfile1DAdjuster(factor=0.5),
    'LogParabola1D':              _LineProfile1DAdjuster(factor=0.5),
}


# Functions can have parameter names that are similar but not quite the same.
_p_names = {
    'Gaussian1D':                 {'amplitude': 'amplitude', 'position': 'mean', 'width': 'stddev'},
    'GaussianAbsorption1D':       {'amplitude': 'amplitude', 'position': 'mean', 'width': 'stddev'},
    'Beta1D':                     {'amplitude': 'amplitude', 'position': 'x_0'},
    'Lorentz1D':                  {'amplitude': 'amplitude', 'position': 'x_0', 'width': 'fwhm'},
    'Box1D':                      {'amplitude': 'amplitude', 'position': 'x_0', 'width': 'width'},
    'MexicanHat1D':               {'amplitude': 'amplitude', 'position': 'x_0', 'width': 'sigma'},
    'Trapezoid1D':                {'amplitude': 'amplitude', 'position': 'x_0', 'width': 'width'},
    'PowerLaw1D':                 {'amplitude': 'amplitude', 'position': 'x_0'},
    'BrokenPowerLaw1D':           {'amplitude': 'amplitude', 'position': 'x_break'},
    'ExponentialCutoffPowerLaw1D':{'amplitude': 'amplitude', 'position': 'x_0'},
    'LogParabola1D':              {'amplitude': 'amplitude', 'position': 'x_0'},
    }


# Main function. X and Y are for now numpy arrays with the
# independent and dependent variables. It's assumed X values
# are stored in increasing order in the array.
def adjust(instance, x, y):
    if x is None or y is None:
        return instance

    name = models_registry.getComponentName(instance)
    try:
        adjuster = _adjusters[name]
        return adjuster.adjust(instance, x, y)
    except KeyError:
        return instance
