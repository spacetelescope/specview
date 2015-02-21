from PyQt4 import QtGui, QtCore, Qt


class BaseToolBar(QtGui.QToolBar):
    def __init__(self, parent=None):
        super(BaseToolBar, self).__init__(parent)
        self.setFloatable(False)
        self.setMovable(False)
        # self.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)

        self.atn_insert_region = QtGui.QAction("&Insert \nROI", self)
        self.atn_insert_region.setIcon(QtGui.QIcon("./qt/img/rect_select.png"))
        self.atn_insert_region.setToolTip('Add rectangular region-of-interest')

        # Setup buttons
        self.addAction(self.atn_insert_region)
        self.addSeparator()


class SpectraToolBar(BaseToolBar):
    def __init__(self, parent=None):
        super(SpectraToolBar, self).__init__(parent)

        self.button_insert_region = QtGui.QAction('&Insert Region', self)
        self.button_insert_region.setStatusTip('Add rectangular region-of-interest')

        self.button_fit_region = QtGui.QAction('&Fit Region', self)
        self.button_fit_region.setStatusTip('Fit rectangular '
                                               'region-of-interest')

        self.active_plots = QtGui.QAction('&Active Plot', self)
        self.active_plots.setStatusTip('Select visible plots.')

        self.active_plot_menu = QtGui.QMenu("Active Plot Menu", self)


class ImageToolBar(BaseToolBar):

    def __init__(self):
        super(ImageToolBar, self).__init__()