from PyQt4 import QtGui, QtCore, Qt


class BaseToolBar(QtGui.QToolBar):
    def __init__(self, parent=None):
        super(BaseToolBar, self).__init__(parent)
        self.setFloatable(False)
        self.setMovable(False)
        # self.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)

        self.atn_insert_roi = QtGui.QAction("&Insert \nROI", self)
        self.atn_insert_roi.setIcon(QtGui.QIcon("./qt/img/rect_select.png"))
        self.atn_insert_roi.setToolTip('Add rectangular region-of-interest')

        # Setup buttons
        self.addAction(self.atn_insert_roi)
        self.addSeparator()


class SpectraToolBar(BaseToolBar):
    def __init__(self, parent=None):
        super(SpectraToolBar, self).__init__(parent)

        self.atn_model_editor = QtGui.QAction("&Model Editor", self)
        self.atn_model_editor.setIcon(QtGui.QIcon("./qt/img/rect_select.png"))
        self.atn_model_editor.setToolTip('Opens the model editor')

        self.addAction(self.atn_model_editor)

        self.active_plots = QtGui.QAction('&Active Plot', self)
        self.active_plots.setStatusTip('Select visible plots.')

        self.active_plot_menu = QtGui.QMenu("Active Plot Menu", self)


class ImageToolBar(BaseToolBar):
    def __init__(self):
        super(ImageToolBar, self).__init__()