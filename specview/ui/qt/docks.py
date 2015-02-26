from PyQt4 import QtGui, QtCore, Qt
from pyqtgraph.console import ConsoleWidget
from specview.ui.qt.tree_views import SpectrumDataTree, ModelTree


class BaseDockWidget(QtGui.QDockWidget):
    """Subclass of dock widget."""
    def __init__(self):
        super(BaseDockWidget, self).__init__()

        # Set empty main widget with layout
        main_widget = QtGui.QWidget()
        self.vb_layout = QtGui.QVBoxLayout()
        main_widget.setLayout(self.vb_layout)

        # Set main window
        self.setWidget(main_widget)

    def add_widget(self, widget):
        self.vb_layout.addWidget(widget)

    def add_layout(self, layout):
        self.vb_layout.addLayout(layout)


class DataDockWidget(BaseDockWidget):
    def __init__(self):
        super(DataDockWidget, self).__init__()
        self.setWindowTitle("Data")

        # Set allowed areas and behavior
        self.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea |
                             QtCore.Qt.RightDockWidgetArea)

        # Add TreeView widget
        self.wgt_data_tree = SpectrumDataTree()
        self.wgt_data_tree.setSelectionMode(
            QtGui.QAbstractItemView.ExtendedSelection)

        # Set Plotting buttons
        self.btn_create_plot = QtGui.QToolButton()
        self.btn_create_plot.setIcon(QtGui.QIcon("./qt/img/new_plot.png"))
        self.btn_add_plot = QtGui.QToolButton()
        self.btn_add_plot.setIcon(QtGui.QIcon("./qt/img/insert_plot.png"))

        # Arithmetic buttons
        self.btn_sum = QtGui.QToolButton()
        self.btn_sum.setIcon(QtGui.QIcon("./qt/img/add.png"))
        self.btn_diff = QtGui.QToolButton()
        self.btn_diff.setIcon(QtGui.QIcon("./qt/img/subtract.png"))
        self.btn_mult = QtGui.QToolButton()
        self.btn_mult.setIcon(QtGui.QIcon("./qt/img/multiply.png"))
        self.btn_div = QtGui.QToolButton()
        self.btn_div.setIcon(QtGui.QIcon("./qt/img/divide.png"))

        # Add to main layout
        self.add_widget(self.wgt_data_tree)

        # Setup buttons
        hb_layout = QtGui.QHBoxLayout()
        hb_layout.addWidget(self.btn_create_plot)
        hb_layout.addWidget(self.btn_add_plot)
        hb_layout.addStretch()
        hb_layout.addWidget(self.btn_sum)
        hb_layout.addWidget(self.btn_diff)
        hb_layout.addWidget(self.btn_mult)
        hb_layout.addWidget(self.btn_div)

        self.add_layout(hb_layout)


class InfoDockWidget(BaseDockWidget):
    def __init__(self):
        super(InfoDockWidget, self).__init__()
        self.setWindowTitle("Info")

        self.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea |
                             QtCore.Qt.RightDockWidgetArea)

        self.wgt_text_edit = QtGui.QTextEdit()

        self.add_widget(self.wgt_text_edit)


class ConsoleDockWidget(BaseDockWidget):
    def __init__(self):
        super(ConsoleDockWidget, self).__init__()
        self.setWindowTitle("Console")

        self.setAllowedAreas(QtCore.Qt.BottomDockWidgetArea)

        self.wgt_console = ConsoleWidget()

        self.add_widget(self.wgt_console)

        self.setVisible(False)


class ModelDockWidget(BaseDockWidget):
    """
    TODO: make dedicated class for handling getting/retrieving selected model
    data, and to handle creating the ModelViewItem instance.
    """
    from specview.analysis import model_fitting

    def __init__(self):
        super(ModelDockWidget, self).__init__()

        self.setWindowTitle("Model Editor")

        self.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea |
                             QtCore.Qt.RightDockWidgetArea)

        # Create TreeView widget
        self.wgt_model_tree = ModelTree()
        self.wgt_model_tree.setSelectionMode(
            QtGui.QAbstractItemView.ExtendedSelection)

        # Create combo box for fitting selections
        self.wgt_model_selector = QtGui.QComboBox()
        self.wgt_model_selector.addItems(self.model_fitting.all_models.keys())

        # Create add model button
        self.btn_add_model = QtGui.QToolButton()

        # Create horizontal layout for combo box + button
        hb_layout = QtGui.QHBoxLayout()
        hb_layout.addWidget(self.wgt_model_selector)
        hb_layout.addWidget(self.btn_add_model)

        self.add_layout(hb_layout)
        self.add_widget(self.wgt_model_tree)

        self.btn_fit_model = QtGui.QPushButton()

        # self.add_widget(self.btn_fit_model)

        # Create combo box for selecting fitter
        self.wgt_fit_selector = QtGui.QComboBox()
        self.wgt_fit_selector.addItems(self.model_fitting.all_fitters.keys())

        # Create button for performing fit
        self.btn_perform_fit = QtGui.QPushButton("&Fit")

        self.add_widget(self.wgt_fit_selector)
        self.add_widget(self.btn_perform_fit)
