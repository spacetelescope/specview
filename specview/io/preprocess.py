from astropy.io import fits
from specview.core import SpectrumData, SpectrumArray


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
