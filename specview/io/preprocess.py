from astropy.io import fits
from specview.core import SpectrumData

def read_table(table,
               dispersion='wavelength', flux='flux',
               dispersion_unit='angstrom', flux_unit='count/s'):
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

    table_dispersion_unit = None
    table_flux_unit = None
    try:
        table_dispersion_unit = table.columns[table.names.index(dispersion)].unit
    except ValueError:
        pass
    try:
        flux_unit = table.columns[table.names.index(flux)].unit
    except ValueError:
        pass
    if table_dispersion_unit is not None:
        dispersion_unit = table_dispersion_unit
    if table_flux_unit is not None:
        flux_unit = table_flux_unit

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
