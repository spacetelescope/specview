import warnings
from astropy.wcs import WCS
from astropy.io import fits
from astropy.io.fits.hdu.image import _ImageBaseHDU as FITS_image
from astropy.io.fits.hdu.table import _TableLikeHDU as FITS_table
# from specview.core import SpectrumData
from cube_tools.core import SpectrumData

DEFAULT_FLUX_UNIT = 'count'
DEFAULT_DISPERSION_UNIT = 'pixel'


def read_image(image, flux_unit=None, dispersion_unit=None, **kwargs):
    """Read 1D image

    Parameters
    ----------
    image: FITS Image HDU

    Returns
    -------
    SpectrumData

    Notes
    -----
    Assumes ONLY 1D and that the WCS has the dispersion
    definition. If not, its just pixels.
    """
    if len(image.data.shape) > 1:
        raise RuntimeError('Attempting to read an image with more than one '
                           'dimension.')
    wcs = WCS(image.header)
    spectrum = SpectrumData()
    unit = flux_unit if flux_unit else DEFAULT_FLUX_UNIT
    spectrum.set_y(image.data, unit=unit)
    unit = wcs.wcs.cunit[0] if not dispersion_unit else dispersion_unit
    spectrum.set_x(wcs.all_pix2world(range(image.data.shape[0]), 1)[0],
                   unit=unit)

    return spectrum


def read_table(table,
               flux='flux', dispersion='wavelength',
               flux_unit=None, dispersion_unit=None):
    """Read FITS table

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

    Returns
    -------
    SpectrumData
    '"""
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


def read_data(file_name, ext=None, **kwargs):
    """Simple function to read in a file and retrieve extensions that
    contain data.

    Parameters
    ----------
    file_name : str
        File name of FITS data object.

    ext: int
        Extension to read. If none, the first one with data will be used.

    kwargs: dict
        Keyword arguments to pass to helper routines.
    """
    if ".fits" in file_name:
        name = file_name.split("/")[-1].split(".")[-1]
        hdulist = fits.open(str(file_name))

        exts = [ext] if ext is not None else range(len(hdulist))
        for idx in exts:
            if isinstance(hdulist[idx], FITS_table):
                try:
                    data = read_table(hdulist[idx].data, **kwargs)
                    return data
                except Exception as e:
                    warnings.warn('File {}[{}]: {}'.format(file_name, idx, e.args[0]))
            elif isinstance(hdulist[idx], FITS_image):
                try:
                    data = read_image(hdulist[idx], **kwargs)
                    return data
                except Exception as e:
                    warnings.warn('File {}[{}]: {}'.format(file_name, idx, e.args[0]))

        raise RuntimeError('File {} does not contain any supported 1D format.'.format(file_name))
