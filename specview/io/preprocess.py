from astropy.io import fits
from specview.core import SpectrumData

def read_table(table,
               flux='flux', dispersion='wavelength',
               flux_unit=None, dispersion_unit=None):
    '''Read FITS table

    Parameters
    ----------
    table: FITS table

    dispersion: str
                Name of column containing the dispersion axis.

    flux: str
          Name of column containing the flux axis.

    dispersion_unit: str
                     Unit of dispersion

    flux_unit: str
               Unit of flux
    '''
    DEFAULT_FLUX_UNIT = 'count'
    DEFAULT_DISPERSION_UNIT = 'pixel'

    if dispersion_unit is None:
        try:
            dispersion_unit = table.columns[table.names.index(dispersion.upper())].unit
            if dispersion_unit is None:
                raise ValueError
        except ValueError:
            dispersion_unit = DEFAULT_DISPERSION_UNIT
    if flux_unit is None:
        try:
            flux_unit = table.columns[table.names.index(flux.upper())].unit
            if flux_unit is None:
                raise ValueError
        except ValueError:
            flux_unit = DEFAULT_FLUX_UNIT

    spectrum = SpectrumData()
    spectrum.set_x(table[dispersion], unit=dispersion_unit)
    spectrum.set_y(table[flux], unit=flux_unit)

    return spectrum

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
        data_collection = []

        for i in range(len(hdulist)):
            if hdulist[i].data.size > 0:
                data = hdulist[i].data
                data_collection.append(data)

        return name, data_collection
