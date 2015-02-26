import re
from astropy.io import fits
from astropy.io.fits.hdu.table import _TableLikeHDU as FITS_table

def deep21dconvert(hdul_in, separate=True):
    '''Convert a DEEP2 1D spectra to a more normalized spectra

    Parameters
    ----------
    hdul_in: fits.HDUList
        The original HDUList of a DEEP2 extracted spectrum.

    separate: bool
        If true, separate the extensions into separate HDUList's

    Returns
    -------
        A list of HDULists. If separate is False, a list of
        one is returned.
    '''
    ARRAY_COLUMNS = set(['SPEC',
                         'LAMBDA',
                         'IVAR',
                         'CRMASK',
                         'BITMASK',
                         'ORMASK',
                         'NBADPIX',
                         'INFOMASK',
                         'SKYSPEC'])

    hdu_primary = fits.PrimaryHDU(header=hdul_in[0].header)

    bin_hdus = []
    for ext in range(len(hdul_in)):
        if isinstance(hdul_in[ext], FITS_table):
            cols_new = fits.ColDefs([])
            for col in hdul_in[ext].columns:
                data = col.array
                format = re.match('\d*(\D.*)', col.format).group(1)
                unit = None
                if col.name in ARRAY_COLUMNS:
                    data = col.array[0]
                if col.name == 'SPEC':
                    unit = 'ct/h'
                if col.name == 'LAMBDA':
                    unit = 'angstrom'
                col_new = fits.Column(array=data,
                                      name=col.name,
                                      format=format,
                                      unit=unit)
                cols_new.add_col(col_new)
            bin_hdus.append(fits.BinTableHDU.from_columns(cols_new))

    result = []
    if separate:
        for bin_hdu in bin_hdus:
            result.append(fits.HDUList([hdu_primary, bin_hdu]))
    else:
        result.append(fits.HDUList([hdu_primary].extend(bin_hdus)))

    return result

def column_copy(column):
    '''Copy a column fixing the format'''
    new = column.copy()
    new.format = re.match('\d*(\D.*)', column.format).group(1)
    return new
