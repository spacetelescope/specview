from astropy.io import fits
from specview.core import SpectrumData, SpectrumArray
import numpy as np
from astropy.units import Unit
import random


def read_data(file_name):
    """Simple function to read in a file and retrieve extensions that
    contain data.

    Parameters
    ----------
    file_name : str
        File name of data object.
    """
    if ".fits" in file_name:
        name = file_name.split("/")[-1].split(".")[-1]
        hdulist = fits.open(str(file_name))
        x_unit = hdulist['SCI'].header['TUNIT1']
        y_unit = hdulist['SCI'].header['TUNIT2']
        data = hdulist['SCI'].data
        x, y = data['WAVELENGTH'], data['FLUX']

        spec_data = SpectrumData()
        spec_data.set_x(x, unit=Unit('angstrom'))
        spec_data.set_y(y, unit=Unit('flm'))

        return spec_data
