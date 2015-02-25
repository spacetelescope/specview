from astropy.io import fits
import numpy as np

def califa_convert(hdul_in):
    '''Separate out CALIFA data using WCS'''

    # Setup the header.
    hdu_primary_header = fits.Header()
    hdu_primary_header['CRVAL1'] = hdul_in[0].header['CRVAL3']
    hdu_primary_header['CDELT1'] = hdul_in[0].header['CDELT3']
    hdu_primary_header['CRPIX1'] = hdul_in[0].header['CRPIX3']
    hdu_primary_header['WCSAXES'] = 1
    hdu_primary_header['WCSNAME'] = 'SPECTRAL'
    hdu_primary_header['CTYPE1'] = hdul_in[0].header['CTYPE3']
    hdu_primary_header['CUNIT1'] = hdul_in[0].header['CUNIT3']
    hdu_primary_header['CD1_1']  = hdul_in[0].header['CD3_3']

    # Setup the input data to be iterated over.
    spectrum_len, image_ydim, image_xdim = hdul_in[0].data.shape
    nspec = image_xdim * image_ydim
    image_in = np.reshape(hdul_in[0].data, (spectrum_len, nspec))

    # Extract
    hdu_images = []
    for idx in range(nspec):
        hdu = fits.PrimaryHDU(data=image_in[:, idx],
                              header=hdu_primary_header)
        hdu_images.append(hdu)

    return hdu_images
