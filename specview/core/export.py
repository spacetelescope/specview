from astropy.io import fits


def export_fits(data_item, path=None):
    data = data_item.item

    data_hdu = fits.ImageHDU(data.data, name='data')
    ivar_hdu = fits.ImageHDU(data.uncertainty.array, name='ivar')
    mask_hdu = fits.ImageHDU(data.mask.astype(int), name='mask')

    prihdu = fits.Header.fromstring(data.wcs.wcs.print_contents())

    thdulist = fits.HDUList([prihdu, data_hdu, ivar_hdu, mask_hdu])
    thdulist.writeto('~/{}'.format(path if path is not None else
                                   data_item.name))
