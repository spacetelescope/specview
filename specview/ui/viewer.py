from __future__ import print_function

from ..external.qt import QtGui, QtCore
from .qt.menubars import MainMenuBar
from .qt.toolbars import BaseToolBar
from .qt.docks import (DataDockWidget, MeasurementDockWidget,
                       ConsoleDockWidget, ModelDockWidget,
                       EquivalentWidthDockWidget)
from .qt.subwindows import SpectraMdiSubWindow
from .items import LayerDataTreeItem


class MainWindow(QtGui.QMainWindow):
    sig_view_current_changed = QtCore.Signal()
    sig_view_selected_changed = QtCore.Signal()

    def __init__(self, show_console=True):
        super(MainWindow, self).__init__()
        # Basic app info
        self.show_console = show_console
        self.menu_bar = MainMenuBar()
        self.setMenuBar(self.menu_bar)
        self.setWindowTitle('SpecPy')
        self.tool_bar = BaseToolBar()
        self.addToolBar(self.tool_bar)

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
        # self.model_editor_dock.hide()

        # Setup equivalent width dock
        self.equiv_width_dock = EquivalentWidthDockWidget(self)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea,
                           self.equiv_width_dock)
        self.equiv_width_dock.hide()

        # setup
        self.setup_signal_relay()
        self.connect_signals()

    def setup_signal_relay(self):
        # When a layer item is selected, send a signal that the current
        # layer item has changed
        self.data_dock.wgt_layer_tree.sig_current_changed.connect(
            self.sig_view_selected_changed.emit)

        # When a data item is selected, send a signal that the current data
        # item has changed
        self.data_dock.wgt_data_tree.sig_current_changed.connect(
            self.sig_view_current_changed.emit)

    def connect_signals(self):
        # Enable/disable toolbar actions depending on what is selected in
        # the views
        self.sig_view_current_changed.connect(lambda:
            self.tool_bar.toggle_actions(self.current_data_item is not None,
                                         self.current_layer_item is not None))

        # When a data item is selected, update the layer item view to
        # reflect all layers under the data item
        self.data_dock.wgt_data_tree.sig_current_changed.connect(
            self.data_dock.wgt_layer_tree.set_root_index)

        self.data_dock.wgt_layer_tree.sig_current_changed.connect(
            self.model_editor_dock.wgt_model_tree.set_root_index)

    def set_view_models(self, default, data, layers):
        self.model_editor_dock.wgt_model_tree.setModel(default)
        self.data_dock.wgt_data_tree.setModel(data)
        self.data_dock.wgt_layer_tree.setModel(layers)

    @property
    def all_graphs(self):
        return [sw.graph for sw in self.mdiarea.subWindowList()]

    @property
    def current_layer_item(self):
        return self.data_dock.wgt_layer_tree.current_item

    @property
    def current_data_item(self):
        return self.data_dock.wgt_data_tree.current_item

    @property
    def selected_model(self):
        return str(self.model_editor_dock.wgt_model_selector.currentText())

    @property
    def selected_fitter(self):
        return str(self.model_editor_dock.wgt_fit_selector.currentText())

    def set_layer_visibity(self, layer_data_item, show):
        for graph in self.all_graphs:
            graph.set_visibility(layer_data_item, show)

    def new_sub_window(self, layer_data_item, set_active=True,
                       style='line'):
        sub_window = self.mdiarea.addSubWindow(SpectraMdiSubWindow())
        sub_window.plot_toolbar.atn_model_editor.triggered.connect(lambda:
            self.model_editor_dock.setVisible(self.model_editor_dock.isHidden()))
        sub_window.show()

        sub_window.graph.add_item(layer_data_item)

    def remove_graph(self, layer_data_item, sub_window=None):
        if not isinstance(layer_data_item, LayerDataTreeItem):
            return

        if sub_window is None:
            sub_window = self.viewer.mdiarea.activeSubWindow()

        sub_window.graph.remove_item(layer_data_item)
