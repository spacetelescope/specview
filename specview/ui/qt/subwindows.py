from astropy.units import Unit

from ...external.qt import QtGui, QtCore
# from PySide import QtGui, QtCore
from .graphs import Graph2D, SpectraGraph, Graph1D
from .toolbars import (ImageToolBar, SpectraToolBar, SpectraPlotToolBar,
                       MOSToolBar)
import pyqtgraph as pg


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

        self.graph = Graph2D()
        self.toolbar = ImageToolBar()

        self.vb_layout.addWidget(self.toolbar)
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
        self.plot_toolbar.atn_insert_roi.triggered.connect(self.graph.add_roi)
        # self.plot_toolbar.atn_equiv_width.triggered.connect()

    def _connect_tools(self):
        self.plot_toolbar.unit_dialog.accepted.connect(
            self._update_graph_units)

        self.plot_toolbar.top_axis_dialog.accepted.connect(
            self._update_graph_top_axis)

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

    def _update_graph_top_axis(self):
        top_axis_dialog = self.plot_toolbar.top_axis_dialog
        self.graph._top_axis.set_mode(top_axis_dialog.mode,
                                      ref_wavelength=top_axis_dialog.ref_wave,
                                      redshift=top_axis_dialog.redshift)

    def _toggle_graph_step(self):
        pass


class MultiMdiSubWindow(BaseMdiSubWindow):
    def __init__(self, parent=None):
        super(MultiMdiSubWindow, self).__init__(parent)
        import numpy as np
        self.graph1d = Graph1D()
        self.graph1d.set_plot(y=np.random.normal(size=(100)))
        self.graph2d = Graph2D()
        self.graph2d.set_image(np.random.normal(size=(100, 10)))
        self.graph_postage = Graph2D()
        self.toolbar = MOSToolBar()
        # self.test_iv = pg.ImageView(view=pg.PlotItem())
        # self.test_iv.setImage(np.random.sample(size=(100, 100)))

        self.info_area = QtGui.QLabel()
        self.info_area.setFrameStyle(QtGui.QFrame.Panel)
        self.info_area.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        self.info_area.setScaledContents(True)

        # Set margins
        self.info_area.setContentsMargins(10, 2, 2, 2)
        self.graph1d.setContentsMargins(2, 2, 2, 2)
        self.graph2d.setContentsMargins(2, 2, 2, 2)
        self.graph_postage.setContentsMargins(2, 2, 2, 2)

        # Setup linked views
        self.graph2d.setXLink(self.graph1d)
        # self.graph2d.setYLink(self.graph_postage)

        self.vb_layout.addWidget(self.toolbar)

        hb_layout = QtGui.QSplitter()
        self.vb_layout.addWidget(hb_layout)

        right_split = QtGui.QSplitter(QtCore.Qt.Vertical)
        left_split = QtGui.QSplitter(QtCore.Qt.Vertical)

        hb_layout.addWidget(left_split)
        hb_layout.addWidget(right_split)

        left_split.addWidget(self.graph_postage)
        left_split.addWidget(self.info_area)
        right_split.addWidget(self.graph2d)
        right_split.addWidget(self.graph1d)

        hb_layout.setStretchFactor(0, 1)
        hb_layout.setStretchFactor(1, 3)

        left_split.setStretchFactor(0, 1)
        left_split.setStretchFactor(1, 3)

        right_split.setStretchFactor(0, 1)
        right_split.setStretchFactor(1, 3)

        # self.grid = QtGui.QGridLayout()
        # self.vb_layout.addLayout(self.grid)
        #
        # self.grid.addWidget(self.graph_postage, 0, 0)
        # self.grid.addWidget(self.graph2d, 0, 1)
        # self.grid.addWidget(self.info_area, 1, 0)
        # self.grid.addWidget(self.graph1d, 1, 1)
        #
        # self.grid.setColumnStretch(0, 1)
        # self.grid.setRowStretch(0, 1)
        # self.grid.setColumnStretch(1, 3)
        # self.grid.setRowStretch(1, 3)

    def set_image_data(self, data):
        self.graph_postage.set_image(data)

    def set_graph2d_data(self, data):
        self.graph2d.set_image(data)

    def set_graph1d_data(self, data):
        self.graph1d.set_plot(y=data)

    def set_items(self, items):
        # if len(items) > 1:
        self.toolbar.enable_all(True)
        self.toolbar.set_item_names(items.keys())

        first_item = items.items()[0]

        self.set_image_data(first_item[1]['img'])
        self.set_graph2d_data(first_item[1]['2d'])
        self.set_graph1d_data(first_item[1]['1d'])

    def set_label(self, table):
        t = ""
        print("setting label")
        for k, v in table.items():
            print(k, v)
            t += "<tr><th align='left'>{}</th><td>{}</td></tr>".format(str(k),
                                                                       str(v))
        self.info_area.setText("""
<h3>Information</h3><br />
<table>{}
</table>
""".format(t))