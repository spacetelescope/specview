from PyQt4 import QtGui, QtCore, Qt


class BaseToolBar(QtGui.QToolBar):
    def __init__(self, parent=None):
        super(BaseToolBar, self).__init__(parent)
        self.setFloatable(False)
        self.setMovable(False)


class SpectraToolBar(BaseToolBar):
    def __init__(self, parent=None):
        super(SpectraToolBar, self).__init__(parent)

        self.button_insert_region = QtGui.QAction('&Insert Region', self)
        self.button_insert_region.setStatusTip('Add rectangular region-of-interest')

        self.button_delete_region = QtGui.QAction('&Delete Region', self)
        self.button_delete_region.setStatusTip('Remove rectangular '
                                               'region-of-interest')

        self.button_fit_region = QtGui.QAction('&Fit Region', self)
        self.button_fit_region.setStatusTip('Fit rectangular '
                                               'region-of-interest')

        self.setup_buttons()

    def setup_buttons(self):
        self.addAction(self.button_insert_region)
        self.addAction(self.button_delete_region)
        self.addAction(self.button_fit_region)
        self.addSeparator()


class ImageToolBar(BaseToolBar):

    def __init__(self):
        super(ImageToolBar, self).__init__()