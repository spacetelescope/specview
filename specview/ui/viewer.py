from PyQt4 import QtGui, QtCore

from specview.ui.qt.menubars import MainMainBar
from specview.ui.qt.docks import (DataDockWidget, MeasurementDockWidget,
                                  ConsoleDockWidget, ModelDockWidget,
                                  EquivalentWidthDockWidget)


class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        # Basic app info
        self.menu_bar = MainMainBar()
        self.setMenuBar(self.menu_bar)
        self.setWindowTitle('SpecPy')
        tb = QtGui.QToolBar()
        self.addToolBar(tb)
        tb.hide()

        # File open dialog
        self.file_dialog = QtGui.QFileDialog(self)

        # Set the MDI area as the central widget
        self.mdiarea = QtGui.QMdiArea(self)
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
        self.data_dock = DataDockWidget(self)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.data_dock)

        # Setup measurement dock
        self.measurement_dock = MeasurementDockWidget(self)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.measurement_dock)
        self.measurement_dock.hide()

        # Setup model dock
        self.model_editor_dock = ModelDockWidget(self)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea,
                           self.model_editor_dock)
        self.model_editor_dock.setFloating(True)
        self.model_editor_dock.hide()

        # Setup equivalent width dock
        self.equiv_width_dock = EquivalentWidthDockWidget(self)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea,
                           self.model_editor_dock)
        self.equiv_width_dock.setFloating(True)
        self.equiv_width_dock.hide()

        # Setup console dock
        self.console_dock = ConsoleDockWidget(self)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, self.console_dock)

        self._setup_menu_bar()

    def _setup_menu_bar(self):
        self.menu_bar.window_menu.addAction(
            self.data_dock.toggleViewAction())
        self.menu_bar.window_menu.addAction(
            self.measurement_dock.toggleViewAction())
        # self.menu_bar.docks_menu.addAction(
        #     self.equiv_width_dock.toggleViewAction())
        self.menu_bar.window_menu.addAction(
            self.console_dock.toggleViewAction())

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