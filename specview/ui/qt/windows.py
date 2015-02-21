from PyQt4 import QtGui, QtCore
from pyqtgraph.console import ConsoleWidget

from specview.ui.qt.menubars import MenuBar
from specview.ui.qt.toolbars import SpectraToolBar
from custom import SpecViewModel
from widgets import (DataDockWidget, InfoDockWidget, ConsoleDockWidget)


class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        # Basic app info
        self.menu_bar = MenuBar()
        self.setMenuBar(self.menu_bar)
        self.setWindowTitle('IFUpy')
        self.addToolBar("")

        # Set the MDI area as the central widget
        self.mdiarea = QtGui.QMdiArea()
        self.mdiarea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.mdiarea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.mdiarea.setActivationOrder(QtGui.QMdiArea.CreationOrder)
        self.mdiarea.cascadeSubWindows()

        # Set center widget as a top-level, layout-ed widget
        main_layout = QtGui.QVBoxLayout()
        main_layout.addWidget(self.mdiarea)
        main_layout.setContentsMargins(0, 0, 0, 0)
        # self.setCentralWidget(main_widget)
        self.setCentralWidget(self.mdiarea)
        self.setCorner(QtCore.Qt.BottomRightCorner,
                       QtCore.Qt.RightDockWidgetArea)

        # Setup data dock
        self.dock_data = DataDockWidget()
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.dock_data)

        # Setup info view dock
        self.dock_info = InfoDockWidget()
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.dock_info)

        # Setup console dock
        self.dock_console = ConsoleDockWidget()
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, self.dock_console)

    def _hide_toolbars(self):
        for child in self.children():
            if isinstance(child, QtGui.QToolBar):
                self.removeToolBar(child)
