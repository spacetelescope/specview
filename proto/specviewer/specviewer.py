import logging
#logging.basicConfig(level=logging.DEBUG)

from PyQt4.QtGui import QMainWindow

from pyqt_nonblock import pyqtapplication
from spectrum_view import SpectrumView
from specview_signals import Signal, Signals
from specview_ui import Ui_MainWindow

class SpecViewer(QMainWindow):

    app = None

    def __init__(self, parent=None):

        if self.__class__.app is None:
            self.__class__.app = pyqtapplication()
            if not getattr(self.__class__.app, '_svs_signals', None):
                self.__class__.app._svs_signals = Signals(signal_class=Signal)
        self.signals = self.__class__.app._svs_signals

        super(SpecViewer, self).__init__(parent=parent)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.view = (SpectrumView(parent=self))

        self.setCentralWidget(self.view)

        self.show()

    def connect(self, signals):
        self.signals = signals

if __name__ == '__main__':
    sv = SpecViewer()
    sv.app.exec_()
