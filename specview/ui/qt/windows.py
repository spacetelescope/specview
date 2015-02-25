from PyQt4 import QtGui, QtCore
from pyqtgraph.console import ConsoleWidget

from specview.ui.qt.menubars import MainMainBar
from specview.ui.qt.toolbars import SpectraToolBar
from models import SpectrumDataTreeModel
from docks import (DataDockWidget, InfoDockWidget, ConsoleDockWidget,
               ModelDockWidget)


class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        # Basic app info
        self.menu_bar = MainMainBar()
        self.setMenuBar(self.menu_bar)
        self.setWindowTitle('IFUpy')
        tb = QtGui.QToolBar()
        self.addToolBar(tb)
        tb.hide()

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
        self.dock_info.hide()

        # Setup info view dock
        self.dock_model_editor = ModelDockWidget()
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.dock_model_editor)
        self.dock_model_editor.setFloating(True)
        self.dock_model_editor.hide()

        # Setup console dock
        self.dock_console = ConsoleDockWidget()
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, self.dock_console)

    def set_toolbar(self, toolbar=None, hide_all=False):
        if toolbar is not None:
            self.addToolBar(toolbar)

        for child in self.children():
            if isinstance(child, QtGui.QToolBar):
                if child == toolbar:
                    child.show()
                elif child.isVisible():
                    child.hide()

                if hide_all:
                    child.hide()