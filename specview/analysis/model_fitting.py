import numpy as np
from astropy.modeling import models, fitting

all_models = {
    'Gaussian1D': models.Gaussian1D,
    'GaussianAbsorption1D': models.GaussianAbsorption1D,
    'Lorentz1D': models.Lorentz1D,
    'MexicanHat1D': models.MexicanHat1D,
    'Trapezoid1D': models.Trapezoid1D,
    'ExponentialCutoffPowerLaw1D': models.ExponentialCutoffPowerLaw1D,
    'BrokenPowerLaw1D': models.BrokenPowerLaw1D,
    'LogParabola1D': models.LogParabola1D,
    'PowerLaw1D': models.PowerLaw1D,
    'Linear1D': models.Linear1D,
    'Const1D': models.Const1D,
    'Redshift': models.Redshift,
    'Scale': models.Scale,
    'Shift': models.Shift,
    'Sine1D': models.Sine1D,
    'Chebyshev1D': models.Chebyshev1D,
    'Legendre1D': models.Legendre1D,
    'Polynomial1D': models.Polynomial1D,
}

all_fitters = {
    'Levenberg-Marquardt': fitting.LevMarLSQFitter,
}


def get_model(name):
    if name not in all_models.keys():
        raise NameError("There is no model named {}".format(name))

    return all_models[name]()


def get_fitter(name):
    if name not in all_fitters.keys():
        raise NameError("There is no fitter named {}".format(name))

    return all_fitters[name]()


def gaussian(x, y):
    amp, mean, stddev = _gaussian_parameter_estimates(x, y)
    g_init = models.Gaussian1D(amplitude=amp, mean=mean, stddev=stddev)
    fit_g = fitting.LevMarLSQFitter()
    g = fit_g(g_init, x, y)

    return (g.amplitude, g.mean, g.stddev), x, g(x)


def _gaussian_parameter_estimates(x, y, dy=0):
    amplitude = np.percentile(y, 95)
    y = np.max(y / y.sum(), 0)
    mean = (x * y).sum()
    stddev = np.sqrt((y * (x - mean) ** 2).sum())
    return amplitude, mean, stddev

