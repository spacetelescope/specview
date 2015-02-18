import six
import numpy as np
from astropy.modeling.fitting import LevMarLSQFitter

from specview.proto.specviewer.spectrum_data import SpectrumData


def fit(spectra):
    models = []
    raw = []
    for name, spectrum_entry in six.iteritems(spectra):
        spectrum = spectrum_entry['spectrum']
        try:
            models.append(spectrum.model())
        except AttributeError:
            raw.append(spectrum)

    fitter = LevMarLSQFitter()
    fits = []
    for model in models:
        for spectrum in raw:
            flux = spectrum.data.copy()
            fit_sum = np.zeros(len(flux))
            for transform in model._transforms:
                fit = fitter(transform, spectrum.wcs, flux)(spectrum.wcs)
                flux -= fit
                fit_sum += fit
            fits.append((spectrum.wcs, fit_sum))

    for nfit, fit in enumerate(fits):
        fit_spectrum = SpectrumData('Fit{}'.format(nfit),
                                    fit[1],
                                    wcs=fit[0])
        spectra.add(fit_spectrum)
