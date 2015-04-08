from os import sys, path
from PyQt4 import QtGui
import astropy.extern.six


def main():
    app = QtGui.QApplication(sys.argv)
    app_gui = Controller()
    app_gui.viewer.show()

    sys.exit(app.exec_())


if __name__ == '__main__' and __package__ is None:
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    from specview.ui.controller import Controller

    main()