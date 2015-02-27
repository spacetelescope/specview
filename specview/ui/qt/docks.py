from os import sys, path

from PyQt4 import QtGui, QtCore
from pyqtgraph.console import ConsoleWidget

from specview.ui.qt.tree_views import SpectrumDataTree, ModelTree
from specview.analysis import model_fitting

PATH = path.join(path.dirname(sys.modules[__name__].__file__), "img")


class BaseDockWidget(QtGui.QDockWidget):
    """Subclass of dock widget."""
    def __init__(self, parent=None):
        super(BaseDockWidget, self).__init__(parent)

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
    def __init__(self, parent=None):
        super(DataDockWidget, self).__init__(parent)
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
        self.btn_create_plot.setIcon(QtGui.QIcon(
            path.join(PATH, "new_plot.png")))
        self.btn_add_plot = QtGui.QToolButton()
        self.btn_add_plot.setIcon(QtGui.QIcon(path.join(PATH,
                                                        "insert_plot.png")))

        # Add to main layout
        self.add_widget(self.wgt_data_tree)

        # Setup buttons
        hb_layout = QtGui.QHBoxLayout()
        hb_layout.addWidget(self.btn_create_plot)
        hb_layout.addWidget(self.btn_add_plot)
        hb_layout.addStretch()

        self.add_layout(hb_layout)


class InfoDockWidget(BaseDockWidget):
    def __init__(self, parent=None):
        super(InfoDockWidget, self).__init__(parent)
        self.setWindowTitle("Info")

        self.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea |
                             QtCore.Qt.RightDockWidgetArea)

        self.lbl_layer = QtGui.QLabel()
        self.lbl_mean = QtGui.QLabel()
        self.lbl_median = QtGui.QLabel()
        self.lbl_stddev = QtGui.QLabel()
        self.lbl_total = QtGui.QLabel()

        form_layout = QtGui.QFormLayout()
        form_layout.addWidget(self.lbl_layer)
        form_layout.addRow(self.tr("Mean:"), self.lbl_mean)
        form_layout.addRow(self.tr("Median:"), self.lbl_median)
        form_layout.addRow(self.tr("Std. Dev.:"), self.lbl_stddev)
        form_layout.addRow(self.tr("Total:"), self.lbl_total)

        group_box = QtGui.QGroupBox("Statistics")
        group_box.setLayout(form_layout)

        self.add_widget(group_box)

    def set_labels(self, stats, name=""):
        self.lbl_layer.setText(name)
        self.lbl_mean.setText(str(stats['mean']))
        self.lbl_median.setText(str(stats['median']))
        self.lbl_stddev.setText(str(stats['stddev']))
        self.lbl_total.setText(str(stats['total']))


class ConsoleDockWidget(BaseDockWidget):
    def __init__(self, parent=None):
        super(ConsoleDockWidget, self).__init__(parent)
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

    def __init__(self, parent=None):
        super(ModelDockWidget, self).__init__(parent)

        self.setWindowTitle("Model Editor")

        self.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea |
                             QtCore.Qt.RightDockWidgetArea)

        # Create TreeView widget
        self.wgt_model_tree = ModelTree()
        self.wgt_model_tree.setSelectionMode(
            QtGui.QAbstractItemView.ExtendedSelection)

        # Create combo box for fitting selections
        self.wgt_model_selector = QtGui.QComboBox()
        self.wgt_model_selector.addItems(model_fitting.all_models.keys())

        # Create add model button
        self.btn_add_model = QtGui.QToolButton()

        # Create horizontal layout for combo box + button
        hb_layout = QtGui.QHBoxLayout()
        hb_layout.addWidget(self.wgt_model_selector)
        hb_layout.addWidget(self.btn_add_model)

        # Create combo box for selecting fitter
        self.wgt_fit_selector = QtGui.QComboBox()
        self.wgt_fit_selector.addItems(model_fitting.all_fitters.keys())

        # Create button for performing fit
        self.btn_perform_fit = QtGui.QPushButton("&Fit Model to Data")

        self.add_layout(hb_layout)
        self.add_widget(self.wgt_model_tree)
        self.add_widget(self.wgt_fit_selector)
        self.add_widget(self.btn_perform_fit)
