from os import sys
import numpy as np

# from PyQt4 import QtGui, QtCore
from specview.external.qt import QtGui, QtCore

from astropy.modeling import fitting
from specview.tools import model_io as mio
from specview.tools import model_registry as mr

class Example(QtGui.QWidget):
    def __init__(self, argv):
        super(Example, self).__init__()

        fitter = fitting.LevMarLSQFitter()
        x = np.array([100.,400.,800.,1200.,1500.,1800.,2100.,2400.])
        y = np.array([0.,50.,200.,400.,300.,200.,100.,10.])

        compound_model, directory = mio.buildModelFromFile("/Users/busko/atest6.py")
        print("Compound model after first read: ")
        print(compound_model)
        print("and _submodels after first read look like this: ")
        print(mr.getComponents(compound_model))

        # window = QtGui.QMainWindow()
        # window.show()
        # parameter = QtGui.QStandardItem('TEST')
        # window.add(parameter)
        # parameter.setData(1.2345)

        cb = QtGui.QCheckBox('Show title', self)
        cb.move(20, 20)
        cb.toggle()
        cb.stateChanged.connect(self.changeTitle)

        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('QtGui.QCheckBox')
        self.show()

        result = fitter(compound_model, x, y)
        print("Fitted results: ")
        print(result)

        compound_model, directory = mio.buildModelFromFile("/Users/busko/atest6.py")
        print("Compound model after second read: ")
        print(compound_model)
        print("and _submodels after second read look like this: ")
        print(mr.getComponents(compound_model))

    def changeTitle(self, state):
        if state == QtCore.Qt.Checked:
            self.setWindowTitle('QtGui.QCheckBox')
        else:
            self.setWindowTitle('')

def run():
    app = QtGui.QApplication(sys.argv)
    win = Example(sys.argv)
    app.connect(app, QtCore.SIGNAL("lastWindowClosed()"),
                app, QtCore.SLOT("quit()"))
    app.exec_()

if __name__ == '__main__':
    run()
