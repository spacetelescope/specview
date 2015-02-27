from PyQt4 import QtGui
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

        self.atn_model_editor = QtGui.QAction("&Model Editor", self)
        self.atn_model_editor.setIcon(QtGui.QIcon(path.join(PATH,
                                                            "model_editor.png")))
        self.atn_model_editor.setToolTip('Opens the model editor')

        self.addAction(self.atn_model_editor)

        self.atn_measure = QtGui.QAction("&Measurements", self)
        self.atn_measure.setIcon(QtGui.QIcon(path.join(PATH, "info_rect.png")))
        self.atn_measure.setToolTip('Get measurements from current region')

        self.addAction(self.atn_measure)


class SpectraPlotToolBar(QtGui.QToolBar):
    def __init__(self, parent=None):
        super(SpectraPlotToolBar, self).__init__(parent)

        self.atn_edit_units = QtGui.QAction("&Change Units", self)
        self.atn_edit_units.setToolTip("Convert the plot units")

        self.addAction(self.atn_edit_units)
        self.atn_edit_units.triggered.connect(self._show_edit_units)

    def _show_edit_units(self):
        dialog = PlotUnitsDialog()
        dialog.exec_()

class ImageToolBar(BaseToolBar):
    def __init__(self):
        super(ImageToolBar, self).__init__()