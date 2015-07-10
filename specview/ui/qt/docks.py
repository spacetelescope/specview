from os import sys, path

from specview.external.qt import QtGui, QtCore
from pyqtgraph.console import ConsoleWidget
from IPython.qt.console.rich_ipython_widget import RichIPythonWidget

from specview.ui.qt.boxes import StatisticsGroupBox
from specview.ui.qt.views import SpectrumDataTree, ModelTree, LayerDataTree
from specview.analysis import model_fitting

QPUSHBUTTON_CSS = """QPushButton {
                         border: 0px solid #8f8f91;
                         border-radius: 4px;
                     }

                     QPushButton:pressed {
                         background-color: qlineargradient(
                             x1: 0, y1: 0, x2: 0, y2: 1,
                             stop: 0 #dadbde, stop: 1 #f6f7fa
                         );
                     }

                     QPushButton:hover {
                         border: 1px solid #999;
                         border-radius: 4px;
                     }"""


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

        # Set allowed areas and behavior
        self.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea |
                             QtCore.Qt.RightDockWidgetArea)

        # Create data sets TreeView widget
        self.wgt_data_tree = SpectrumDataTree()
        self.wgt_data_tree.setSelectionMode(
            QtGui.QAbstractItemView.ExtendedSelection)

        # Create data layers TreeView widget
        self.wgt_layer_tree = LayerDataTree()
        self.wgt_layer_tree.setSelectionMode(
            QtGui.QAbstractItemView.ExtendedSelection)

        # Create Label widget
        self.lbl_data_sets = QtGui.QLabel("Data Sets")
        self.lbl_data_layers = QtGui.QLabel("Data Layers")

        # Circituitous means
        lyt_data_tree = QtGui.QVBoxLayout()
        lyt_data_tree.setContentsMargins(0,0,0,10)
        wgt_data_tree_main = QtGui.QWidget()
        wgt_data_tree_main.setLayout(lyt_data_tree)
        lyt_data_tree.addWidget(self.lbl_data_sets)
        lyt_data_tree.addWidget(self.wgt_data_tree)

        lyt_layer_tree = QtGui.QVBoxLayout()
        lyt_layer_tree.setContentsMargins(0,10,0,0)
        wgt_layer_tree_main = QtGui.QWidget()
        wgt_layer_tree_main.setLayout(lyt_layer_tree)
        lyt_layer_tree.addWidget(self.lbl_data_layers)
        lyt_layer_tree.addWidget(self.wgt_layer_tree)

        # Splitter object
        self.spl_data = QtGui.QSplitter()
        self.spl_data.setOrientation(QtCore.Qt.Vertical)
        self.spl_data.addWidget(wgt_data_tree_main)
        self.spl_data.addWidget(wgt_layer_tree_main)

        self.add_widget(self.spl_data)

        # Add to main layout
        # self.add_widget(self.lbl_data_sets)
        # self.add_widget(self.wgt_data_tree)
        # self.add_widget(self.lbl_data_layers)
        # self.add_widget(self.wgt_layer_tree)


class MeasurementDockWidget(BaseDockWidget):
    def __init__(self, parent=None):
        super(MeasurementDockWidget, self).__init__(parent)
        self.setWindowTitle("Measurement Info")

        self.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea |
                             QtCore.Qt.RightDockWidgetArea)

        self.lbl_data_set = QtGui.QLabel()
        self.lbl_layer = QtGui.QLabel()

        title_form_layout = QtGui.QFormLayout()
        title_form_layout.addRow(self.tr("Data set:"), self.lbl_data_set)
        title_form_layout.addRow(self.tr("Layer:"), self.lbl_layer)

        # Measurements tab
        self.measurement_stats_box = StatisticsGroupBox("Statistics")

        self.add_layout(title_form_layout)
        self.add_widget(self.measurement_stats_box)

    def set_labels(self, stats, data_name="", layer_name=""):
        self.lbl_data_set.setText(data_name)
        self.lbl_layer.setText(layer_name)
        self.measurement_stats_box.set_labels(stats)


class EquivalentWidthDockWidget(BaseDockWidget):
    def __init__(self, parent=None):
        super(EquivalentWidthDockWidget, self).__init__(parent)
        self.setWindowTitle("Equivalent Width")

        self.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea |
                             QtCore.Qt.RightDockWidgetArea)

        self.lbl_data_set = QtGui.QLabel()
        self.lbl_layer = QtGui.QLabel()

        title_form_layout = QtGui.QFormLayout()
        title_form_layout.addRow(self.tr("Data set:"), self.lbl_data_set)
        title_form_layout.addRow(self.tr("Layer:"), self.lbl_layer)

        # Equivalent width tab
        self.stats_box1 = StatisticsGroupBox("Statistics 1")
        self.stats_box2 = StatisticsGroupBox("Statistics 2")
        self.lbl_equiv_width = QtGui.QLabel()

        ew_form_layout = QtGui.QFormLayout()

        ew_form_layout.addRow(self.tr("Equivalent Width:"),
                              self.lbl_equiv_width)

        self.add_layout(title_form_layout)
        self.add_widget(self.stats_box1)
        self.add_widget(self.stats_box2)
        self.add_layout(ew_form_layout)

    def set_labels(self, value, stats1, stats2, data_name="", layer_name=""):
        self.lbl_data_set.setText(data_name)
        self.lbl_layer.setText(layer_name)
        self.stats_box1.set_labels(stats1)
        self.stats_box2.set_labels(stats2)
        self.lbl_equiv_width.setText(str(value))


class ConsoleDockWidget(BaseDockWidget):
    def __init__(self, parent=None):
        super(ConsoleDockWidget, self).__init__(parent)
        self.setWindowTitle("Console")

        self.setAllowedAreas(QtCore.Qt.BottomDockWidgetArea)

        self.wgt_console = RichIPythonWidget()

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
        # self.btn_add_model = QtGui.QToolButton()

        # Create horizontal layout for combo box + button
        # hb_layout = QtGui.QHBoxLayout()
        # hb_layout.addWidget(self.wgt_model_selector)
        # hb_layout.addWidget(self.btn_add_model)

        # Create combo box for selecting fitter
        self.wgt_fit_selector = QtGui.QComboBox()
        self.wgt_fit_selector.addItems(model_fitting.all_fitters.keys())

        # Create button for performing fit
        self.btn_perform_fit = QtGui.QPushButton("&Fit Model")

        # self.add_layout(hb_layout)
        self.add_widget(self.wgt_model_selector)
        self.add_widget(self.wgt_model_tree)
        self.add_widget(self.wgt_fit_selector)
        self.add_widget(self.btn_perform_fit)
        self.setMinimumSize(self.sizeHint())
