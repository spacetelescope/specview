import numpy as np
from astropy.nddata import (NDData, NDSlicingMixin, NDArithmeticMixin)
from astropy.wcs import WCS
from astropy.units import Unit


class SpectrumArray(NDSlicingMixin, NDArithmeticMixin, NDData):
    """
    Basic container for spectrum data.

    Contains additional metadata such as uncertainties, a mask, units,
    and/or coordinate system.
    """
    def __init__(self, *args, **kwargs):
        super(SpectrumArray, self).__init__(*args, **kwargs)

    @property
    def shape(self):
        return self.data.shape

    @property
    def data(self):
        if self.mask is None:
            return super(SpectrumArray, self).data
        else:
            return super(SpectrumArray, self).data[np.logical_not(self.mask)]


class SpectrumData(object):
    """
    Contains exactly two `SpectrumArray` objects; one for flux, the other
    for wavelength.
    """
    def __init__(self, x=None, y=None):
        self._x = x
        self._y = y
        self._layers = []

    def set_x(self, data, wcs=None, unit=None, name=""):
        if not isinstance(wcs, WCS) and wcs is not None:
            raise TypeError("wcs object is not of type WCS.")

        self._x = SpectrumArray(data, wcs=wcs, unit=unit)

    def set_y(self, data, wcs=None, unit=None, name=""):
        if not isinstance(wcs, WCS) and wcs is not None:
            raise TypeError("wcs object is not of type WCS.")

        self._y = SpectrumArray(data, wcs=wcs, unit=unit)

    def add_layer(self, mask):
        self._layers.append(Layer(self, mask))

    def remove_layer(self, layer):
        self._layers.remove(layer)

    @property
    def models(self):
        return self._models

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @property
    def shape(self):
        return self.x.shape[0], self.y.shape[0]

    @property
    def mask(self):
        return self.x.mask

    @mask.setter
    def mask(self, value):
        print("Setting mask")
        print(value)
        self.x.mask = value
        self.y.mask = value


class Layer(object):
    """
    Layer objects contain a masked array of the original data. They can also
    contain any number of model objects.
    """
    def __init__(self, parent, mask):
        self._parent = parent
        self._mask = mask

        self.data = np.ma.array(parent, mask=mask)
        self._models = []

    def add_model(self, model):
        self._models.append(model)


class ImageArray(NDSlicingMixin, NDArithmeticMixin, NDData):
    """
    Basic container for image data.

    Contains additional metadata such as uncertaintier, a mask, units,
    and/or coordinate system.
    """
    def __init__(self, *args, **kwargs):
        super(ImageArray, self).__init__(*args, **kwargs)

    @property
    def shape(self):
        return self._data.shape


class CubeData():
    """
    Container object for IFU cube data. The internal data unit for the data
    array is whatever unit the counts are in. That is, the unit for this
    object is not an axis unit, per say.
    """
    def __init__(self, *args, **kwargs):
        super(CubeData, self).__init__(*args, **kwargs)
        self._units = [Unit(''), Unit(''), Unit('')]

    @property
    def units(self):
        return self._units

    def set_unit(self, index, unit):
        """Sets the unit of the dimension specified by `index`."""
        if not isinstance(unit, Unit):
            unit = Unit(unit)

        self._units[index] = unit

    def set_units(self, unit0, unit1, unit2):
        self._units = [unit0, unit1, unit2]

    @property
    def shape(self):
        return self._data.shape



if __name__ == '__main__':
    arr = np.random.normal(size=10)
    sdarr = SpectrumData(arr)
    sdarr2 = SpectrumData(np.random.normal(size=10))
    print(sdarr.add(sdarr2))