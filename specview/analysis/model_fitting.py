import numpy as np
from astropy.modeling import models, fitting
from cube_tools.core.data_objects import SpectrumData

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


def _updateLayerItem(new_model, layer_data_item):
    for model_idx in range(layer_data_item.rowCount()):
        model_data_item = layer_data_item.child(model_idx)

        for param_idx in range(model_data_item.rowCount()):
            parameter_data_item = model_data_item.child(param_idx, 1)

            if layer_data_item.rowCount() > 1:
                value = new_model[model_idx].parameters[param_idx]
            else:
                value = new_model.parameters[param_idx]
            #TODO the following setData, when executed, messes up
            # with the compound model in such a way that it can never
            # be updated again by importing from a file. We leave it
            # commented out, but wondering if this will have any
            # further implication down the road.
            # Mmm...yes, it will. Commenting out this statement makes
            # parameter values impossible to change via user edits.
            # It looks like when setData is executed, a signal gets
            # propagated somewhere, and reaches rogue code that
            # causes the model to break when importing from file.

            # parameter_data_item.setData(value)

            parameter_data_item.setText(str(value))


def fit_model(layer_data_item, fitter_name, roi_mask):
    if len(layer_data_item._model_items) == 0:
        return

    fitter = get_fitter(fitter_name)

    init_model = layer_data_item.model

    print("@@@@@@  file model_fitting.py; line 85 - initial model:  "), init_model

    x, y = layer_data_item.item.dispersion, layer_data_item.item.flux

    fitted_model = fitter(init_model, x.value[roi_mask], y.value[roi_mask])

    print("@@@@@@  file model_fitting.py; line 91 -  fitted model:  "), fitted_model


    new_y = fitted_model(x.value[roi_mask])

    # It was decided not to carry around dispersion data, instead
    # letting it be calculated. This means we have to maintain the same
    # array shape because we don't always know at what dispersion value
    # a flux array starts
    tran_y = np.empty(shape=x.value.shape)
    tran_y[roi_mask] = new_y
    tran_y[~roi_mask] = 0.0
    new_y = tran_y

    # Create new data object
    fit_spec_data = SpectrumData(new_y, unit=layer_data_item.item.unit,
                                 mask=layer_data_item.item.mask,
                                 wcs=layer_data_item.item.wcs,
                                 meta=layer_data_item.item.meta,
                                 uncertainty=None)

    # Update using model approach
    _updateLayerItem(fitted_model, layer_data_item)

    return fit_spec_data