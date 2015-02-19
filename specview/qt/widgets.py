from PyQt4 import QtGui, QtCore, Qt


class TreeWidget(QtGui.QTreeWidget):
    def __init__(self):
        super(TreeWidget, self).__init__()

    def get_current_viewer(self):
        return self.currentItem()