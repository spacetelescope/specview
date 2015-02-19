from PyQt4 import QtGui, QtCore, Qt
from menubars import MenuBar
import pyqtgraph as pg
from pyqtgraph.console import ConsoleWidget


class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        # Basic app info
        self.menu_bar = None
        self.statusBar().showMessage('Ready')
        self.setWindowTitle('IFUpy')

        # Set the MDI area as the central widget
        self.mdiarea = QtGui.QMdiArea()
        self.mdiarea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.mdiarea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.mdiarea.setActivationOrder(QtGui.QMdiArea.CreationOrder)
        self.mdiarea.cascadeSubWindows()
        self.mdiarea.show()

        # Set center widget as a top-level, layout-ed widget
        main_widget = QtGui.QWidget()
        main_layout = QtGui.QVBoxLayout()
        main_widget.setLayout(main_layout)
        main_layout.addWidget(self.mdiarea)
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.setCentralWidget(main_widget)
        self.setCorner(QtCore.Qt.BottomRightCorner,
                       QtCore.Qt.RightDockWidgetArea)

        # Setup tree view dock
        self.dock_tree_view = QtGui.QDockWidget("Data Sets", self)
        self.widget_tree_view_data = None
        self.button_add_plot = None
        self.setup_dock_tree_view_data()

        # Setup info view dock
        self.dock_info_view = QtGui.QDockWidget("Info View", self)
        self.widget_text_edit_view = None
        self.setup_dock_info_view()

        # Setup console dock
        self.dock_console = QtGui.QDockWidget("Console", self)
        self.widget_console = None
        self.setup_dock_console()
        self.dock_console.setVisible(False)

        # Add them as tool box tabs
        self.setup_menu_bar()
        self.show()

    def setup_menu_bar(self):
        self.menu_bar = MenuBar()
        self.setMenuBar(self.menu_bar)

    def setup_dock_tree_view_data(self):
        self.dock_tree_view.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea
                                  | QtCore.Qt.RightDockWidgetArea)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.dock_tree_view)

        dd_widget = QtGui.QWidget()
        dd_layout = QtGui.QVBoxLayout()
        dd_widget.setLayout(dd_layout)

        # Tree view widget
        self.widget_tree_view_data = QtGui.QTreeWidget()
        self.widget_tree_view_data.setDragEnabled(True)
        self.widget_tree_view_data.setColumnCount(2)
        self.widget_tree_view_data.setHeaderLabels(QtCore.QStringList(["Name",
                                                                "Shape"]))

        # Button widget
        self.button_add_plot = QtGui.QPushButton("&Plot")

        dd_layout.addWidget(self.widget_tree_view_data)
        dd_layout.addWidget(self.button_add_plot)

        self.dock_tree_view.setWidget(dd_widget)

    def setup_dock_info_view(self):
        self.dock_info_view.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea
                                  | QtCore.Qt.RightDockWidgetArea)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.dock_info_view)

        iv_widget = QtGui.QWidget()
        iv_layout = QtGui.QVBoxLayout()
        iv_widget.setLayout(iv_layout)

        self.widget_text_edit_view = QtGui.QTextEdit()

        iv_layout.addWidget(self.widget_text_edit_view)

        self.dock_info_view.setWidget(iv_widget)

    def setup_dock_console(self):
        self.dock_console.setAllowedAreas(QtCore.Qt.BottomDockWidgetArea)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, self.dock_console)

        con_widget = QtGui.QWidget()
        con_layout = QtGui.QVBoxLayout()
        con_widget.setLayout(con_layout)

        self.widget_console = ConsoleWidget()

        con_layout.addWidget(self.widget_console)

        self.dock_console.setWidget(con_widget)