from __future__ import print_function

import sys

import astropy
import astropy.units as u

from specview.core import SpectrumData

'''
Units converter.

We still need to find out (in the Java specview's code)
how these can be defined:
    1/micron
    km/s @ 21cm
    km/s @ 12 CO (11.5 GHz)
    Rayleigh/Angstrom
    ABmag

'''

class UnitsConverter(object):
    ''' Convert wave and flux arrays to target units.

    Parameters
    ----------
    wunit: Unit instance
      target unit for the spectral coordinate array
    funit: Unit instance
      target unit for the flux array
    '''

    def __init__(self, wunit, funit):
        self._wunit = wunit
        self._funit = funit

    def convertSpectrumData(self, sp_data, exception=False):
        ''' Convert in-place a SpectrumData instance to target units.

        Parameters
        ----------
        sp_data: SpectrumData
          SpectrumData instance to be converted
        exception: boolean, optional, default=False
          if False, a units conversion exception will result in an
          error message being printed at the console. If True, the
          error message is printed AND the exception is raised again.
          This behavior helps in debugging scripts.

        '''
        # Curiously, we have to force the SpectrumData input arrays into
        # the Quantity format (via multiplication by the unit instance),
        # so they can inherit a to() unit conversion method. Why not make
        # the SpectrumData arrays Quantity themselves, from the constructor
        # on?
        wave = sp_data.x.data * sp_data.x.unit
        flux = sp_data.y.data * sp_data.y.unit

        cwave, cflux = converter.convert(wave, flux, exception)

        sp_data.set_x(cwave)
        sp_data.set_y(cflux)

    def convert(self, wave, flux, exception=False):
        ''' Convert arrays to target units.

        Parameters
        ----------
        wave: Quantity
          spectral coordinate array to be converted to target units
        flux: Quantity
          flux array to be converted to target units
        exception: boolean, optional, default=False
          if False, a units conversion exception will result in an
          error message being printed at the console. If True, the
          error message is printed AND the exception is raised again.
          This behavior helps in debugging scripts.

        Returns
        -------
           two Quantity instances with the converted wave and flux arrays.
           In case of error, the original input references are returned.
        '''
        try:
            converted_wave = wave.to(self._wunit, equivalencies=u.spectral())
            converted_flux = flux.to(self._funit, equivalencies=u.spectral_density(wave))

            return converted_wave, converted_flux

        except (ValueError, astropy.units.core.UnitsError) as e:
            print("UNITS CONVERSION ERROR: ", e, file=sys.stderr)
            if exception:
                raise e
            return wave, flux


# Example usage
def print_results(wave, flux, converted_wave, converted_flux):
    for k in range(4):
        print(wave[k], "   ", converted_wave[k])
    for k in range(4):
        print(flux[k], "   ", converted_flux[k])

import test_data

if __name__ == "__main__":
    # real emission line from UV spectrum of NGC3516
    x,y,e = test_data.get_data()


    # test conversions from SpectrumData objects.
    sp_data = SpectrumData()
    sp_data.set_x(x, unit="Angstrom")
    sp_data.set_y(y, unit="erg.s-1.cm**-2.Angstrom-1") # flam

    converter = UnitsConverter(u.micron, u.Jy)
    converter.convertSpectrumData(sp_data)

    print(sp_data.x.unit, "  ", sp_data.y.unit)
    for k in range(4):
        print(sp_data.x.data[k], "   ", sp_data.y.data[k])


    # test conversions from Quantity objects.
    wave = test_data.get_data()[0] * u.Unit('angstrom')
    flux = test_data.get_data()[1] * u.Unit("erg / (Angstrom cm2 s)")

    converter = UnitsConverter(u.micron, u.Jy)
    converted_wave, converted_flux = converter.convert(wave, flux)

    print_results(wave, flux, converted_wave, converted_flux)

    converter = UnitsConverter(u.THz, u.watt / u.m ** 2 / u.Hz)
    converted_wave, converted_flux = converter.convert(wave, flux)

    print_results(wave, flux, converted_wave, converted_flux)

    converter = UnitsConverter(u.eV, u.erg / u.cm ** 2 / u.s)
    converted_wave, converted_flux = converter.convert(wave, flux)

    print_results(wave, flux, converted_wave, converted_flux)

    converter = UnitsConverter(u.eV, u.Jy * u.Hz)
    converted_wave, converted_flux = converter.convert(wave, flux)

    print_results(wave, flux, converted_wave, converted_flux)


    # test error handling.
    converter = UnitsConverter(u.eV, u.m)
    converted_wave, converted_flux = converter.convert(wave, flux)

    converter = UnitsConverter(u.eV, "BLAH")
    try:
        converted_wave, converted_flux = converter.convert(wave, flux, exception=True)
    except (ValueError, astropy.units.core.UnitsError) as e:
        print("Exception ", str(e), " was raised.")
        pass
