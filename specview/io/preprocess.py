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
        name = file_name.split("/")[-1].split(".")[-2]
        hdulist = fits.open(str(file_name))
        start_wave, step_wave = hdulist[0].header['CRVAL1'], \
                                hdulist[0].header['CD1_1']

        start_range = random.randint(0, 5000)

        y = hdulist[0].data[0]  # normalized flux
        end_wave = len(y) * step_wave + start_wave
        x = np.linspace(start_wave, end_wave, len(y))

        spec_data = SpectrumData()
        spec_data.set_x(x[start_range:start_range+1000], unit=Unit("angstrom"))
        spec_data.set_y(y[start_range:start_range+1000], unit=Unit(
            "erg/cm^2/s/angstrom"))

        return spec_data
