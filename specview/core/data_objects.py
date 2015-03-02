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

    def convert_unit_to(self, unit, equivalencies=[]):
        """
        Returns a new `NDData` object whose values have been converted
        to a new unit. Adapted from `compat.py` of Astropy.

        Parameters
        ----------
        unit : `astropy.units.UnitBase` instance or str
            The unit to convert to.
        equivalencies : list of equivalence pairs, optional
           A list of equivalence pairs to try if the units are not
           directly convertible.  See :ref:`unit_equivalencies`.

        Returns
        -------
        result : `~specview.core.data_objects.SpectrumArray`
            The resulting dataset
        Raises
        ------
        UnitsError
            If units are inconsistent.
        """
        if self.unit is None:
            raise ValueError("No unit specified on source data")

        data = self.unit.to(unit, self.data, equivalencies=equivalencies)

        if self.uncertainty is not None:
            uncertainty_values = self.unit.to(unit, self.uncertainty.array,
                                              equivalencies=equivalencies)
            # should work for any uncertainty class
            uncertainty = self.uncertainty.__class__(uncertainty_values)
        else:
            uncertainty = None

        if self.mask is not None:
            new_mask = self.mask.copy()
        else:
            new_mask = None

        # Call __class__ in case we are dealing with an inherited type
        result = self.__class__(data, uncertainty=uncertainty,
                                mask=new_mask,
                                wcs=self.wcs,
                                meta=self.meta, unit=unit)

        return result


class SpectrumData(object):
    """
    Contains exactly two `SpectrumArray` objects; one for flux, the other
    for wavelength.
    """
    def __init__(self, x=None, y=None):
        self._x = x
        self._y = y

    def set_x(self, data, wcs=None, unit=None, name=""):
        if not isinstance(wcs, WCS) and wcs is not None:
            raise TypeError("wcs object is not of type WCS.")

        self._x = SpectrumArray(data, wcs=wcs, unit=unit)

    def set_y(self, data, wcs=None, unit=None, name=""):
        if not isinstance(wcs, WCS) and wcs is not None:
            raise TypeError("wcs object is not of type WCS.")

        self._y = SpectrumArray(data, wcs=wcs, unit=unit)

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
        self.x.mask = value
        self.y.mask = value

    def add(self, operand, propagate_uncertainties=False):
        # new_y = self._y.add(operand.y, propagate_uncertainties)
        a, b = self._fit_shape(self, operand)
        new_y = a.y.add(b.y, propagate_uncertainties)
        return SpectrumData(self._x, new_y)

    def subtract(self, operand, propagate_uncertainties=False):
        # new_y = self._y.subtract(operand.y, propagate_uncertainties)
        a, b = self._fit_shape(self, operand)
        new_y = a.y.subtract(b.y, propagate_uncertainties)
        return SpectrumData(self._x, new_y)

    def multiply(self, operand, propagate_uncertainties=False):
        # new_y = self._y.multiply(operand.y, propagate_uncertainties)
        a, b = self._fit_shape(self, operand, fill=1)
        new_y = a.y.multiply(b.y, propagate_uncertainties)
        return SpectrumData(self._x, new_y)

    def divide(self, operand, propagate_uncertainties=False):
        # new_y = self._y.divide(operand.y, propagate_uncertainties)
        a, b = self._fit_shape(self, operand, fill=1)
        new_y = a.y.divide(b.y, propagate_uncertainties)
        return SpectrumData(self._x, new_y)

    def _fit_shape(self, a, b, fill=0):
        if a.x.shape[0] > b.x.shape[0]:
            # Make y the same shape
            x_start = a.x.data[a.x.data < b.x.data[0]]
            x_end = a.x.data[a.x.data > b.x.data[-1]]
            new_x = np.concatenate((x_start, b.x.data, x_end))

            y_fill = np.empty(new_x.size)
            y_fill.fill(fill)

            y_start = y_fill[new_x < b.x.data[0]]
            y_end = y_fill[new_x > b.x.data[-1]]
            new_y = np.concatenate((y_start, b.y.data, y_end))

            yp = np.interp(a.x.data, new_x, new_y)

            fin_x = a
            fin_y = SpectrumData(SpectrumArray(new_x, unit=b.x.unit, wcs=b.x.wcs),
                                 SpectrumArray(yp, unit=b.y.unit, wcs=b.y.wcs))

        else:
            # Make y the same shape
            x_start = b.x.data[b.x.data < a.x.data[0]]
            x_end = b.x.data[b.x.data > a.x.data[-1]]
            new_x = np.concatenate((x_start, a.x.data, x_end))

            y_fill = np.empty(new_x.size)
            y_fill.fill(fill)

            y_start = y_fill[new_x < a.x.data[0]]
            y_end = y_fill[new_x > a.x.data[-1]]
            new_y = np.concatenate((y_start, a.y.data, y_end))

            yp = np.interp(b.x.data, new_x, new_y)

            fin_x = a
            fin_y = SpectrumData(SpectrumArray(new_x, unit=a.x.unit, wcs=a.x.wcs),
                                 SpectrumArray(yp, unit=a.y.unit, wcs=a.y.wcs))

        return fin_x, fin_y

    def __add__(self, other):
        return self.add(other)

    def __sub__(self, other):
        return self.subtract(other)

    def __mul__(self, other):
        return self.multiply(other)

    def __div__(self, other):
        return self.divide(other)


class ImageArray(NDSlicingMixin, NDArithmeticMixin, NDData):
    """
    Basic container for image data.

    Contains additional metadata such as uncertainties, a mask, units,
    and/or coordinate system.
    """
    def __init__(self, *args, **kwargs):
        super(ImageArray, self).__init__(*args, **kwargs)

    @property
    def shape(self):
        return self.data.shape


class CubeData(NDSlicingMixin, NDArithmeticMixin, NDData):
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
        return self.data.shape


if __name__ == '__main__':
    arr = np.random.normal(size=10)
    sdarr = SpectrumData(arr)
    sdarr2 = SpectrumData(np.random.normal(size=10))
    print(sdarr.add(sdarr2))