import numpy as np
from astropy.vo import samp
from PyQt4.QtGui import QWidget

from debug import msg_debug
from spectrum_view_ui import Ui_mainView
import spectrum_data as sd

class SpectrumView(QWidget):
    '''Spectrum viewer.
    '''

    def __init__(self, parent=None):
        super(SpectrumView, self).__init__(parent)

        # Connect us up to the signal handler.
        self.signals = samp.SAMPIntegratedClient(name=self.__class__.__name__,
                                                 description='Spectrum Viewer')
        try:
            self.signals.connect(hub=parent.hub)
        except AttributeError:
            self.signals.connect()

        self.spectra = sd.SpectrumDataStore()
        self.spectra_model = sd.SpectrumDataModel(self.spectra)

        self.ui = Ui_mainView()
        self.ui.setupUi(self)

        # Initialize the plotting
        self.axes = self.ui.plotView.figure.add_subplot(111)

        # Initialize the spectrum manager.
        self.ui.spectraListView.setModel(self.spectra_model)

        # There are two sets of events that need to
        # be watched for:  and Matplotlib
        # events. First hadnle Qt events.
        self.signals.bind_receive_notification('samp.app.new_data', self._draw)
        self.signals.bind_receive_notification('samp.app.viewport_change', self._viewport_change)

        # Handle matplotlib events
        #self.register_callbacks()
        self.axes.callbacks.connect('xlim_changed', self._change_data_range)
        self.axes.callbacks.connect('ylim_changed', self._change_data_range)

    def add_spectrum(self, spectrum):
        self.spectra.append(spectrum)
        self.spectra_model.appendRow(spectrum)
        self.signals.enotify_all('samp.app.new_data')

    def _mpl_event(self, event):
        msg_debug('entered.')
        msg_debug('Event name = "{}"'.format(event.name))

    def _draw(self, *args):
        msg_debug('entered')

        for spectrum in self.spectra:
            flux = np.asarray(spectrum.data)
            self.axes.plot(flux)
        self.ui.plotView.canvas.draw()

    def _change_data_range(self, axes):
        msg_debug('entered')
        msg_debug('Axes: {}'.format(id(axes)))
        xlim_low, xlim_high = axes.get_xlim()
        ylim_low, ylim_high = axes.get_ylim()
        self.signals.enotify_all('samp.app.viewport_change',
                                 xlim_low=str(xlim_low), xlim_high=str(xlim_high),
                                 ylim_low=str(ylim_low), ylim_high=str(ylim_high))

    def _viewport_change(self, private_key, sender_id, msg_id, mtype, params, extra):
        msg_debug('entered.')
        msg_debug('msg info: {} {} {} {} {} {}'.format(private_key,
                                                       sender_id,
                                                       msg_id,
                                                       mtype,
                                                       params,
                                                       extra))
        msg_debug('my id is "{}"'.format(self.signals.get_public_id()))

        xlim_new = (float(params['xlim_low']), float(params['xlim_high']))
        ylim_new = (float(params['ylim_low']), float(params['ylim_high']))
        if sender_id != self.signals.get_public_id():
            try:
                msg_debug('resetting limits.')
                changed = False
                xlim_old = self.axes.get_xlim()
                ylim_old = self.axes.get_ylim()
                msg_debug('xlim_old = "{}", xlim_new = "{}"'.format(xlim_old, xlim_new))
                msg_debug('ylim_old = "{}", ylim_new = "{}"'.format(ylim_old, ylim_new))
                if xlim_new != xlim_old:
                    changed = True
                    self.axes.set_xlim(xlim_new)
                if ylim_new != ylim_old:
                    changed = True
                    self.axes.set_ylim(ylim_new)
                if changed:
                    self.ui.plotView.canvas.draw()
            except Exception as e:
                msg_debug('Exception: {}'.format(sys.exec_info()))
            finally:
                msg_debug('finally.')
                return
        msg_debug('exiting.')
