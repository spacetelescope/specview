from threading import Thread
from time import sleep

from astropy.io import fits

from specview.proto.specviewer.spectrum_data import SpectrumData
from specviewer import SpecViewer


print('Reading data..will take a bit...')
hdulist = fits.open('../../../testdata/CALIFA/DR1/V1200/NGC0036.V1200.rscube.fits.gz')
d1 = SpectrumData("d1", hdulist[0].data[:, 20, 20])
d2 = SpectrumData("d2", hdulist[0].data[:, 30, 20])
d3 = SpectrumData("d3", hdulist[0].data[:, 20, 30])
d4 = SpectrumData("d4", hdulist[0].data[:, 30, 30])

print('Creating viewers...')
sv1 = SpecViewer()
sv2 = SpecViewer()

print('Showing data...')
sv1.view.add_spectrum(d1)
sv2.view.add_spectrum(d2)
sv2.view.add_spectrum(d3)

# <demo> stop
print('Viewport changing...')
class V(Thread):
    def run(self):
        for i in range(0, 1800, 200):
            ii = i + 200
            print('Moving viewport to {}-{}'.format(i, ii))
            sv2.view.axes.set_xlim(i, ii)
            sleep(3)
v = V()
v.start()
