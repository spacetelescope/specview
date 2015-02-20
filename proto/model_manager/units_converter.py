from __future__ import print_function

import sys

import astropy
import astropy.units as u


'''
Units converter  -  work in progress.

Find out in specview's code how these can be defined:
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
