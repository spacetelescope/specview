from astropy.io import fits
from specview.core import SpectrumData, Model

def read_table(file_name, ext=1, dispersion='wavelength', flux='flux', model=None):
    '''Read a fits table'''
    if model is None:
        model = Model()

    if ".fits" in file_name:
        name = file_name.split("/")[-1].split(".")[-2]
        hdulist = fits.open(str(file_name))
        tdata = hdulist[ext].data

        spectrum = SpectrumData()
        spectrum.set_x(tdata[dispersion], unit='angstrom')
        spectrum.set_y(tdata[flux], unit='erg/s')
        model.data_items[name] = spectrum

    return model

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
