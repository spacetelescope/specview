import sys
sys.path.insert(1, '../specviewer')
import numpy as np
from astropy.modeling.models import Gaussian1D
from sp_model_manager import ModelManager
from specview.proto.specviewer.specviewer import SpecViewer
from specview.proto.specviewer.spectrum_data import SpectrumData
from fit import fit

# Generate fake data
np.random.seed(0)
x = np.linspace(-5., 5., 200)
y = 3 * np.exp(-0.5 * (x - 1.3)**2 / 0.8**2) + (x / 2.0)
y += np.random.normal(0., 0.2, x.shape)
d1 = SpectrumData('d1', y, wcs=x)

# Setup the model
mm = ModelManager(model=[Gaussian1D(amplitude=1.0, mean=0.5, stddev=0.2)])

sv = SpecViewer()
sv.view.add_spectrum(d1)
sv.view.add_model(mm.model, 'mm')

fit(sv.view.spectra)
sv.signals.ModelAdded()
