from astropy.io import fits

from specview.proto.specviewer.spectrum_data import SpectrumData


hdulist = fits.open('../../testdata/CALIFA/DR1/V1200/NGC0036.V1200.rscube.fits.gz')
d1 = SpectrumData("d1", hdulist[0].data[:, 20, 20])
d2 = SpectrumData("d2", hdulist[0].data[:, 30, 20])
d3 = SpectrumData("d3", hdulist[0].data[:, 20, 30])
d4 = SpectrumData("d4", hdulist[0].data[:, 30, 30])

#sv1 = SpecViewer()
#sv2 = SpecViewer()
