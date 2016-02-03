from os import sys
import numpy as np

# from PyQt4 import QtGui, QtCore
from specview.external.qt import QtGui, QtCore

from astropy.modeling import fitting
from specview.tools import model_io as mio
from specview.tools import model_registry as mr

class Example(object):
    def __init__(self, argv):
        super(Example, self).__init__()

        fitter = fitting.LevMarLSQFitter()
        x = np.array([3.95,4.00,4.05,4.1,4.15,4.20,4.25,4.30])
        y = np.array([0.,0.02,0.05,0.07,0.04,0.02,0.01,0.005])

        compound_model, directory = mio.buildModelFromFile("/Users/busko/atest1.py")
        print("Compound model after first read: ")
        print(compound_model)
        print("and _submodels after first read look like this: ")
        print(mr.getComponents(compound_model))

        # compound_model._submodels[0].amplitude.value = 0.02
        # print("after modifying amplitude_0:  ")
        # print(mr.getComponents(compound_model))
        # print(compound_model)

        result = fitter(compound_model, x, y)
        print("Fitted results: ")
        print(result)

        compound_model, directory = mio.buildModelFromFile("/Users/busko/atest1.py")
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
    app = Example(sys.argv)

if __name__ == '__main__':
    run()
