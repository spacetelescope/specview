from specview.analysis import extract
from specview.core import CubeData, SpectrumData, SpectrumArray
import numpy as np
from astropy.units import Unit
from astropy.modeling import models, fitting


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
        x, y = self._gen_gauss(np.linspace(0.6, 1.1, 100), 20.0, 0.8, 0.01)
        self.spectrum_data1.set_x(x, unit="micron")
        self.spectrum_data1.set_y(y + np.random.normal(size=100), unit="erg/s")

        self.spectrum_data2 = SpectrumData()
        x, y = self._gen_gauss(np.linspace(0.6, 1.1, 100),
                               16.0, 0.94, 0.05)
        self.spectrum_data2.set_x(x, unit="micron")
        self.spectrum_data2.set_y(y + np.random.normal(size=100), unit="erg/s")

        self.spectrum_data3 = SpectrumData()
        x, y = self._gen_gauss(np.linspace(0.6, 1.1, 100), 10.0, 0.65, 0.02)
        self.spectrum_data3.set_x(x, unit="micron")
        self.spectrum_data3.set_y(y + np.random.normal(size=100), unit="erg/s")

        # self.data_items["test1"] = self.cube_data
        self.data_items["test1"] = self.spectrum_data1
        self.data_items["test2"] = self.spectrum_data2
        self.data_items["test3"] = self.spectrum_data3
<<<<<<< HEAD

    def _gen_gauss(self, x, amp, mean, stddev):
        g_init = models.Gaussian1D(amplitude=amp, mean=mean, stddev=stddev)
        return x, g_init(x)
=======
>>>>>>> upstream/master
