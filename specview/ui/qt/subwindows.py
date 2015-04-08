from ...external.qt import QtGui
from astropy.units import Unit

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
        self._connect_tools()

    def _connect_toolbar(self):
        self.toolbar.atn_insert_roi.triggered.connect(self.graph.add_roi)
        # self.toolbar.atn_equiv_width.triggered.connect()

    def _connect_tools(self):
        self.plot_toolbar.unit_dialog.accepted.connect(
            self._update_graph_units)

        self.plot_toolbar.atn_line_style.triggered.connect(lambda:
            self.graph.update_item(style='line'))

        self.plot_toolbar.atn_hist_style.triggered.connect(lambda:
            self.graph.update_item(style='histogram'))

        self.plot_toolbar.atn_scat_style.triggered.connect(lambda:
            self.graph.update_item(style='scatter'))

    def _update_graph_units(self):
        x_unit = self.plot_toolbar.unit_dialog.disp_unit
        y_unit = self.plot_toolbar.unit_dialog.flux_unit

        self.graph.set_units(x=Unit(x_unit) if x_unit is not "" else None,
                             y=Unit(y_unit) if y_unit is not "" else None,
                             z=None)

    def _toggle_graph_step(self):
        pass
