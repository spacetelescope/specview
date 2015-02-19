import logging

import numpy as np

from PyQt4.QtCore import pyqtSignal
from PyQt4.QtGui import QWidget

from spectrum_view_ui import Ui_mainView

import spectrum_data as sd

class SpectrumView(QWidget):
    '''Spectrum viewer.
    '''

    signal_new_data = pyqtSignal()
    signal_viewport_change = pyqtSignal()

    def __init__(self, parent=None):
        super(SpectrumView, self).__init__(parent)

        self.spectra = sd.SpectrumDataStore()
        self.spectra_model = sd.SpectrumDataModel(self.spectra)

        self.ui = Ui_mainView()
        self.ui.setupUi(self)

        # Initialize the plotting
        self.axes = self.ui.plotView.figure.add_subplot(111)

        # Initialize the spectrum manager.
        self.ui.spectraListView.setModel(self.spectra_model)

        # There are two sets of events that need to
        # be watched for: Qt events and Matplotlib
        # events. First hadnle Qt events.
        try:
            self.signal_handler = parent.signal_handler
        except AttributeError:
            self.signal_handler = self

        self.signal_handler.signal_new_data.connect(self._draw)
        self.signal_handler.signal_viewport_change.connect(self._viewport_change)

        # Handle matplotlib events
        #self.register_callbacks()
        self.axes.callbacks.connect('xlim_changed', self._change_data_range)
        self.axes.callbacks.connect('ylim_changed', self._change_data_range)

    def add_spectrum(self, spectrum):
        self.spectra.append(spectrum)
        self.spectra_model.appendRow(spectrum)
        self.signal_handler.signal_new_data.emit()

    def _mpl_event(self, event):
        logging.debug('_mpl_event: entered.')
        logging.debug('_mpl_event: Event name = "{}"'.format(event.name))

    def _draw(self):
        logging.debug('_draw: entered')

        for spectrum in self.spectra:
            flux = np.asarray(spectrum.data)
            self.axes.plot(flux)
        self.ui.plotView.canvas.draw()

    def _change_data_range(self, axes):
        logging.debug('_change_data_range: entered')
        logging.debug('Axes: {}'.format(id(axes)))
        self.signal_handler.signal_viewport_change.emit(self, axes)

    def _viewport_change(self, viewer, axes):
        logging.debug('_viewport_change: entered.')
        logging.debug('_viewport_change: viewer is "{}"'.format(viewer))
        logging.debug('_viewport_change: Sent from myself is "{}"'.format(viewer == self))
        logging.debug('_viewport_change: Axes is "{}"'.format(axes))

        if viewer != self:
            logging.debug('_viewport_change: resetting limits.')
            limits_new = viewer.axes.get_xlim()
            if limits_new != self.axes.get_xlim():
                self.axes.set_xlim(limits_new)
            limits_new = viewer.axes.get_ylim()
            if limits_new != self.axes.get_ylim():
                self.axes.set_ylim(limits_new)
            self.ui.plotView.canvas.draw()
