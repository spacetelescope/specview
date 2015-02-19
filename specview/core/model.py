from specview.analysis import extract
from specview.core import CubeData, SpectrumData, SpectrumArray
from specview.io import read_data
import numpy as np
from astropy.units import Unit


class Model(object):
    """
    A monolithic, centralized interface. We can decide on the details later,
    but there needs to be a temporary single point of entry.
    """
    def __init__(self):
        self.data_items = {}

        self.cube_data = CubeData(np.random.normal(size=(100, 100, 100)))
        self.cube_data.set_units(Unit(''), Unit(''), Unit(''))

        self.spectrum_data1 = SpectrumData()
        self.spectrum_data1.set_x(np.linspace(0.6, 1.1, 100), unit="micron")
        self.spectrum_data1.set_y(np.random.normal(size=100), unit="erg/s")

        self.spectrum_data2 = SpectrumData()
        self.spectrum_data2.set_x(np.linspace(0.6, 1.1, 100), unit="micron")
        self.spectrum_data2.set_y(np.random.normal(size=100), unit="erg/s")

        self.spectrum_data3 = SpectrumData()
        self.spectrum_data3.set_x(np.linspace(0.6, 1.1, 100), unit="micron")
        self.spectrum_data3.set_y(np.random.normal(size=100), unit="erg/s")

        # self.data_items["test1"] = self.cube_data
        self.data_items["test1"] = self.spectrum_data1
        self.data_items["test2"] = self.spectrum_data2
        self.data_items["test3"] = self.spectrum_data3