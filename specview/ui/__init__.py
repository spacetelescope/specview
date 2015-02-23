import sys

from PyQt4 import QtGui

from app_gui import AppGUI

def main(model):
    app = QtGui.QApplication(sys.argv)
    app_gui = AppGUI(model)
    app_gui.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    from specview.core.model import Model
    main(Model())
