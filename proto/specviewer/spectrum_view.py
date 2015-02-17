import six
import warnings

from debug import msg_debug

import numpy as np

from PyQt4.QtGui import QWidget

from spectrum_view_ui import Ui_mainView
from specview_signals import *
from plot_state import PlotState
from spectrum_data import *
from spectrum_model import *


class SpectrumView(QWidget):
    '''Spectrum viewer.
    '''

    def __init__(self, parent=None):
        super(SpectrumView, self).__init__(parent=parent)

        self.spectra = SpectrumDataStore()
        self.spectra_model = SpectrumDataModel(self.spectra)

        self.ui = Ui_mainView()
        self.ui.setupUi(self)

        # Initialize the plotting
        self.axes = self.ui.plotView.figure.add_subplot(111)

        # Initialize the spectrum manager.
        self.ui.spectraListView.setModel(self.spectra_model)

        # There are two sets of events that need to
        # be watched for: Qt events and Matplotlib
        # events. First hadnle Qt events.
        self.signals = getattr(parent, 'signals', Signals(signal_class=Signal))

        self.signals.ModelAdded.connect(self._draw)
        self.signals.ModelRemoved.connect(self._draw)
        self.signals.ModelRefresh.connect(self._refresh)
        self.signals.ViewportChange.connect(self._viewport_change)

        # Handle matplotlib events
        #self.register_callbacks()
        self.axes.callbacks.connect('xlim_changed', self._change_data_range)
        self.axes.callbacks.connect('ylim_changed', self._change_data_range)

    def add_spectrum(self, spectrum):
        spectrum_store = self.spectra.add(spectrum)
        spectrum_store['plot_state'] = PlotState()
        self.spectra_model.add(spectrum)
        self.signals.ModelAdded()

    def remove_spectrum(self, name):
        self.axes.lines.remove(self.spectra[name]['plot_state'].line)
        self.spectra_model.remove(name)
        del self.spectra[name]
        self.signals.ModelRemoved()

    def add_model(self, model, name, *args, **kwargs):
        '''Add an astropy model'''
        if kwargs.get('wcs', None) is None:
            xlow, xhigh = self.axes.get_xlim()
            kwargs['wcs'] = np.arange(xlow, xhigh, (xhigh - xlow) / 100.0)
        spectrum = Model2Spectrum(model, name=name, *args, **kwargs)
        self.add_spectrum(spectrum)

    def remove_model(self, name):
        self.remove_spectrum(name)

    def _mpl_event(self, event):
        msg_debug('entered.')
        msg_debug('Event name = "{}"'.format(event.name))

    def _refresh(self):
        '''Reset plot'''
        for name, spectrum in six.iteritems(self.spectra):
            try:
                spectrum['plot_state'].invalidate()
            except KeyError:
                spectrum['plot_state'] = PlotState()
        self._draw()

    def _draw(self):
        msg_debug('entered')

        for name, spectrum in six.iteritems(self.spectra):
            nddata = spectrum['spectrum']
            flux = np.asarray(nddata.data)
            wcs_array = getattr(nddata, 'wcs', None)
            if wcs_array is None:
                wcs_array = range(len(flux))
            try:
                plot_state = spectrum['plot_state']
            except KeyError:
                spectrum['plot_state'] = PlotState()
                plot_state = spectrum['plot_state']
            if not plot_state.isvalid:
                if plot_state.line:
                    self.axes.lines.remove(plot_state.line)
                plot_state.line = self.axes.plot(wcs_array, flux)[0]
                plot_state.validate()
        self.ui.plotView.canvas.draw()

    def _change_data_range(self, axes):
        msg_debug('entered')
        msg_debug('Axes: {}'.format(id(axes)))
        self.signals.ViewportChange(self, axes)

    def _viewport_change(self, viewer, axes):
        msg_debug('entered.')
        msg_debug('viewer is "{}"'.format(viewer))
        msg_debug('Sent from myself is "{}"'.format(viewer == self))
        msg_debug('Axes is "{}"'.format(axes))

        if viewer != self:
            msg_debug('resetting limits.')
            limits_new = viewer.axes.get_xlim()
            if limits_new != self.axes.get_xlim():
                self.axes.set_xlim(limits_new)
            limits_new = viewer.axes.get_ylim()
            if limits_new != self.axes.get_ylim():
                self.axes.set_ylim(limits_new)
            self.ui.plotView.canvas.draw()
