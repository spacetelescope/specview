from PyQt4 import QtGui, QtCore, Qt


class TreeWidget(QtGui.QTreeWidget):
    def __init__(self):
        super(TreeWidget, self).__init__()

    def get_current_viewer(self):
        return self.currentItem()

    def mouseMoveEvent(self, event):
        item = self.currentItem()
        drag = Qt.QDrag(self)
        mime_data = QtCore.QMimeData()
        mime_data.setText(item.text(0))
        drag.setMimeData(mime_data)
        drag.exec_()