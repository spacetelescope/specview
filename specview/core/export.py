from astropy.io import fits


def export_fits(data_item, path=None):
    data = data_item.item

    tbhdu = fits.BinTableHDU.from_columns([
        fits.Column(name='data', format='20A', array=data.data),
        fits.Column(name='ivar', format='20A', array=data.uncertainty.array),
        fits.Column(name='mask', format='20A', array=data.mask)
    ])

    prihdu = fits.Header.fromstring(data.wcs.print_contents())

    thdulist = fits.HDUList([prihdu, tbhdu])
    thdulist.writeto('~/{}'.format(path if path is not None else
                                   data_item.name))
