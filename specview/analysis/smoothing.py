from astropy.convolution import convolve, convolve_fft
from astropy.convolution import Gaussian1DKernel, Box1DKernel

from cube_tools.core.data_objects import SpectrumData


def spectral_smoothing(spec_data, method='gaussian', **kwargs):

    if method.lower() == 'gaussian':
        g = Gaussian1DKernel(stddev=kwargs['stddev'])
    elif method.lower() == 'boxcar':
        g = Box1DKernel(kwargs['width'])

    if spec_data.data.size > 10000:
        z = convolve_fft(spec_data.data, g)
    else:
        z = convolve(spec_data.data, g)

    new_spec_data = SpectrumData(z, mask=spec_data.mask, wcs=spec_data.wcs,
                                 meta=spec_data.meta, unit=spec_data.unit)

    return new_spec_data