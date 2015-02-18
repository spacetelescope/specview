#logging.basicConfig(level=logging.DEBUG)

from PyQt4.QtCore import pyqtSignal, QObject
from PyQt4.QtGui import QMainWindow

from pyqt_nonblock import pyqtapplication
from spectrum_view import SpectrumView
from specview.proto.specviewer.qt_signals.specview_ui import Ui_MainWindow


class SpecViewer(QMainWindow):

    app = None
    viewers = []
    signal_handler = None

    def __init__(self, parent=None):

        if self.__class__.app is None:
            self.__class__.app = pyqtapplication()
        if self.__class__.signal_handler is None:
            self.__class__.signal_handler = Signals()

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

class Signals(QObject):
    signal_new_data = pyqtSignal()
    signal_viewport_change = pyqtSignal(object, object)

if __name__ == '__main__':
    sv = SpecViewer()
    sv.app.exec_()
