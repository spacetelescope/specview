from PyQt4 import QtCore, QtGui

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar


class MatplotlibWidget(QtGui.QWidget):
    '''Base matplotlib Qt widget'''

    def __init__(self, parent=None, *args, **kwargs):
        super(MatplotlibWidget, self).__init__(parent)
        self.figure = Figure(*args, **kwargs)
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.toolbar = NavigationToolbar(self.canvas, self)
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        self.canvas.draw()
