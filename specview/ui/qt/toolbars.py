from ...external.qt import QtGui, QtCore
from os import sys, path
from specview.ui.qt.dialogs import PlotUnitsDialog

PATH = path.join(path.dirname(sys.modules[__name__].__file__), "img")


class BaseToolBar(QtGui.QToolBar):
    def __init__(self, parent=None):
        super(BaseToolBar, self).__init__(parent)
        self.setFloatable(False)
        self.setMovable(False)
        # self.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)

        self.atn_insert_roi = QtGui.QAction("&Insert \nROI", self)
        self.atn_insert_roi.setIcon(QtGui.QIcon(path.join(PATH,
                                                          "rect_select.png")))
        self.atn_insert_roi.setToolTip('Add rectangular region-of-interest')

        self.atn_create_layer = QtGui.QAction("&Create Layer", self)
        self.atn_create_layer.setIcon(QtGui.QIcon(path.join(PATH,
                                                            "create_layer.png")))
        self.atn_create_layer.setToolTip("Create new layer from ROIs")

        # Setup buttons
        self.addAction(self.atn_insert_roi)
        self.addAction(self.atn_create_layer)
        self.addSeparator()


class SpectraToolBar(BaseToolBar):
    def __init__(self, parent=None):
        super(SpectraToolBar, self).__init__(parent)

        self.atn_measure = QtGui.QAction("&Measurements", self)
        self.atn_measure.setIcon(QtGui.QIcon(path.join(PATH, "info_rect.png")))
        self.atn_measure.setToolTip('Get measurements from current region')

        self.addAction(self.atn_measure)

        self.atn_equiv_width = QtGui.QAction("&Equivalent Width", self)
        self.atn_equiv_width.setIcon(QtGui.QIcon(path.join(PATH,
                                                           "equiv_width.png")))
        self.atn_equiv_width.setToolTip("Calculates equivalent width of the "
                                        "last two ROI regions")

        self.addAction(self.atn_equiv_width)

        self.addSeparator()

        self.atn_model_editor = QtGui.QAction("&Model Editor", self)
        self.atn_model_editor.setIcon(QtGui.QIcon(path.join(PATH,
                                                            "model_editor.png")))
        self.atn_model_editor.setToolTip('Opens the model editor')

        self.addAction(self.atn_model_editor)


class SpectraPlotToolBar(QtGui.QToolBar):
    def __init__(self, parent=None):
        super(SpectraPlotToolBar, self).__init__(parent)
        self.unit_dialog = PlotUnitsDialog()

        plot_opt_menu = QtGui.QMenu()
        layer_opt_menu = QtGui.QMenu()

        # Plot options menu
        self.atn_edit_units = QtGui.QAction("&Change Units", self)
        self.atn_edit_units.setToolTip("Convert the plot units")
        self.atn_edit_units.triggered.connect(self._show_edit_units)

        plot_opt_menu.addAction(self.atn_edit_units)

        # Layer options menu
        self.atn_line_style = QtGui.QAction("&Line", self)
        self.atn_line_style.setToolTip("Render layer with line plot style")

        self.atn_hist_style = QtGui.QAction("&Histogram", self)
        self.atn_hist_style.setToolTip("Render layer in histogram style")

        self.atn_scat_style = QtGui.QAction("&Scatter", self)
        self.atn_scat_style.setToolTip("Render layer in scatter plot style")

        layer_opt_menu.addAction(self.atn_line_style)
        layer_opt_menu.addAction(self.atn_hist_style)
        layer_opt_menu.addAction(self.atn_scat_style)

        # Tool bar menu
        plot_opt_button = QtGui.QToolButton()
        plot_opt_button.setText("&Plot Options")
        plot_opt_button.setPopupMode(QtGui.QToolButton.InstantPopup)
        plot_opt_button.setMenu(plot_opt_menu)

        layer_opt_button = QtGui.QToolButton()
        layer_opt_button.setText("&Layer Options")
        layer_opt_button.setPopupMode(QtGui.QToolButton.InstantPopup)
        layer_opt_button.setMenu(layer_opt_menu)

        self.addWidget(plot_opt_button)
        self.addWidget(layer_opt_button)


    def _show_edit_units(self):
        self.unit_dialog.exec_()


class ImageToolBar(BaseToolBar):
    def __init__(self):
        super(ImageToolBar, self).__init__()
