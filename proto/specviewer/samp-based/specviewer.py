import logging
logging.basicConfig(level=logging.DEBUG)

from PyQt4.QtCore import pyqtSignal, QObject
from PyQt4.QtGui import QMainWindow

from astropy.vo import samp

from pyqt_nonblock import pyqtapplication
from spectrum_view import SpectrumView

from specview_ui import Ui_MainWindow

class SpecViewer(QMainWindow):

    app = None
    viewers = []
    hub = None

    def __init__(self, parent=None):

        if self.__class__.app is None:
            self.__class__.app = pyqtapplication()
        if self.__class__.hub is None:
            self.__class__.hub = Hub()

        super(SpecViewer, self).__init__(parent)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.view = SpectrumView(self)
        self.add_viewer(self.view)

        self.setCentralWidget(self.view)

        self.show()

    def add_viewer(self, viewer):
        #viewer.register_callbacks(self.viewers)
        #for existing_viewer in self.viewers:
        #    existing_viewer.register_callbacks([viewer])
        self.viewers.append(viewer)

class Hub(samp.SAMPHubServer):
    def __init__(self, **kwargs):
        super(Hub, self).__init__(**kwargs)
        self.start()

if __name__ == '__main__':
    sv = SpecViewer()
    sv.app.exec_()
