'''Spectrum Data
'''
from astropy.nddata import NDData #, NDDataBase

class SpectrumData(NDData):
    '''Basic Spectrum'''
    def __init__(self, name, data, *args, **kwargs):
        super(SpectrumData, self).__init__(data, *args, **kwargs)
        self.meta['name'] = name


#class Model2Spectrum(NDDataBase):
class Model2Spectrum(object):
    def __init__(self, model, name,
                 uncertainty=None,
                 mask=None,
                 wcs=None,
                 meta=None,
                 unit=None):
        self.model = model
        self.uncertainty = uncertainty
        self.mask = mask
        self.wcs = wcs
        self.unit = unit
        self.meta = meta

        if self.meta is None:
            self.meta = {}
        self.meta['name'] = name


    @property
    def data(self):
        return self.model()(self.wcs)


class SpectrumDataStore(dict):

    def add(self, spectrum):
        '''Add spectrum to store.

        Parameters
        ----------
        spectrum: SpectrumData
        '''

        spectrum_store = {'spectrum': spectrum}
        self[spectrum.meta['name']] = spectrum_store
        return spectrum_store
