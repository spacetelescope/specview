from specview.external.qt import QtGui


class SpectrumDataContextMenu(QtGui.QMenu):
    def __init__(self, parent=None):
        super(SpectrumDataContextMenu, self).__init__(parent)

        self.atn_remove = QtGui.QAction("&Remove", self)
        self.addAction(self.atn_remove)
