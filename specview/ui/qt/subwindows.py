from PyQt4 import QtGui

from specview.ui.qt.graphs import ImageGraph, SpectraGraph
from specview.ui.qt.toolbars import (ImageToolBar, SpectraToolBar,
                                     SpectraPlotToolBar)


class BaseMdiSubWindow(QtGui.QMdiSubWindow):
    def __init__(self, parent=None):
        super(BaseMdiSubWindow, self).__init__(parent)

        self.sw_widget = QtGui.QWidget()
        self.vb_layout = QtGui.QVBoxLayout()
        self.vb_layout.setContentsMargins(0, 0, 0, 0)
        self.sw_widget.setLayout(self.vb_layout)
        self.setWidget(self.sw_widget)

        self.graph = None
        self.toolbar = None


class ImageMdiSubWindow(BaseMdiSubWindow):
    def __init__(self, parent=None):
        super(ImageMdiSubWindow, self).__init__(parent)

        self.graph = ImageGraph()
        self.toolbar = ImageToolBar()

        # self.vb_layout.addWidget(self.toolbar)
        self.vb_layout.addWidget(self.graph)


class SpectraMdiSubWindow(BaseMdiSubWindow):
    def __init__(self, parent=None):
        super(SpectraMdiSubWindow, self).__init__(parent)
        self.graph = SpectraGraph()
        self.toolbar = SpectraToolBar()
        self.plot_toolbar = SpectraPlotToolBar()

        self.vb_layout.addWidget(self.plot_toolbar)
        self.vb_layout.addWidget(self.graph)

        self._connect_toolbar()

    def _connect_toolbar(self):
        self.toolbar.atn_insert_roi.triggered.connect(self.graph.add_roi)