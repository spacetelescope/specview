import sys

from PyQt4 import QtGui
import numpy as np

from specview.ui.viewer import MainWindow
from specview.ui.model import SpectrumDataTreeModel
from specview.ui.qt import ImageMdiSubWindow, SpectraMdiSubWindow
from specview.io import read_data
from specview.ui.qt.tree_items import LayerDataTreeItem
from specview.analysis.model_fitting import get_fitter
from specview.core.data_objects import SpectrumData, SpectrumArray
from specview.ui.qt.dialogs import FileEditDialog


class Controller(object):
    def __init__(self):
        super(Controller, self).__init__()
        self._model = SpectrumDataTreeModel()
        self._viewer = MainWindow()
        self._viewer.data_dock.wgt_data_tree.setModel(self._model)
        self._viewer.model_editor_dock.wgt_model_tree.setModel(self._model)

        self._connect_trees()
        self._connect_menu_bar()
        self._connect_data_dock()
        self._connect_mdiarea()
        self._connect_model_editor_dock()
        self._connect_active_data()
        self._connect_model_fit()
        self._connect_arithmetic()

        self._viewer.console_dock.wgt_console.localNamespace = {
            'model': self._model,
            'ui': self,
            # 'specview': specview,
            'np': np
        }

    # ---- properties
    @property
    def viewer(self):
        return self._viewer

    @property
    def model(self):
        return self._model

    # ---- protected functions
    def _connect_arithmetic(self):
        self.viewer.data_dock.btn_sum.clicked.connect(lambda:
            self.model.create_data_item(
                np.sum(self.viewer.data_dock.wgt_data_tree.selected_items),
                "Sum"))

    def _connect_model_fit(self):
        self.viewer.model_editor_dock.btn_fit_model.clicked.connect(lambda:
            self.fit_model(
                self.viewer.data_dock.wgt_data_tree.current_item))

    def _connect_active_data(self):
        self.viewer.data_dock.wgt_data_tree.clicked.connect(
            self.update_active_plots)

    def _connect_model_editor_dock(self):
        self.viewer.model_editor_dock.btn_add_model.clicked.connect(
            self._create_model)

        self.viewer.model_editor_dock.btn_perform_fit.clicked.connect(
            self._perform_fit)

    def _connect_trees(self):
        self.viewer.data_dock.wgt_data_tree.clicked.connect(lambda:
            self.viewer.model_editor_dock.wgt_model_tree.set_root_index(
                self.viewer.data_dock.wgt_data_tree.current_item,
                self.viewer.data_dock.wgt_data_tree.currentIndex()
            )
        )

    def _connect_mdiarea(self):
        self.viewer.mdiarea.subWindowActivated.connect(self._set_toolbar)

    def _connect_menu_bar(self):
        self.viewer.menu_bar.atn_open.triggered.connect(self._open_file_dialog)

    def _connect_data_dock(self):
        self._viewer.data_dock.btn_create_plot.clicked.connect(
            self._create_display)
        self._viewer.data_dock.btn_add_plot.clicked.connect(self._display_item)

    def _display_item(self):
        item = self.viewer.data_dock.wgt_data_tree.current_item
        self.display_graph(item)

    def _create_display(self):
        item = self.viewer.data_dock.wgt_data_tree.current_item
        self.create_display(item)

    def _create_layer(self):
        sw = self.viewer.mdiarea.activeSubWindow()

        layer_data_item = self.model.create_layer(
                sw.graph.active_item.parent, sw.graph.active_mask)

        self.display_graph(layer_data_item, sw)

    def _create_model(self):
        self.model.create_fit_model(
            self.viewer.model_editor_dock.wgt_model_tree.active_layer,
            str(self.viewer.model_editor_dock.wgt_model_selector.currentText()))

    def _perform_fit(self):
        fitter_name = self.viewer.model_editor_dock.wgt_fit_selector.currentText()
        fitter = get_fitter(str(fitter_name))

        layer_data_item = self.viewer.data_dock.wgt_data_tree.current_item
        init_model = layer_data_item.model

        x, y = layer_data_item.item.x.data, layer_data_item.item.y.data

        fit_model = fitter(init_model, x, y)
        new_y = fit_model(x)

        # Update using model approach
        for i in range(layer_data_item.rowCount()):
            model_data_item = layer_data_item.child(i)

            for j in range(model_data_item.rowCount()):
                parameter_data_item = model_data_item.child(i, 1)

                if layer_data_item.rowCount() > 1:
                    value = fit_model[i].parameters[j]
                    parameter_data_item.setData(value)
                    parameter_data_item.setText(str(value))
                else:
                    value = fit_model.parameters[j]
                    parameter_data_item.setData(value)
                    parameter_data_item.setText(str(value))

        fit_spec_data = SpectrumData(x=layer_data_item.item.x)
        fit_spec_data.set_y(new_y, wcs=layer_data_item.item.y.wcs,
                            unit=layer_data_item.item.y.unit)

        spec_data_item = self.add_data_set(fit_spec_data, name="Model Fit")
        self.display_graph(spec_data_item)

    def _open_file_dialog(self):
        fname = QtGui.QFileDialog.getOpenFileName(self.viewer, 'Open file')
        self.open_file(fname)

    # ---- public functions
    def update_active_plots(self, index):
        item = self.viewer.data_dock.wgt_data_tree.current_item

        if isinstance(item, LayerDataTreeItem):
            for sub_window in self.viewer.mdiarea.subWindowList():
                sub_window.graph.select_active(item)

    def add_data_set(self, nddata, name="Data", parent=None):
        return self.model.create_data_item(nddata, name)

    def create_display(self, spectrum_data):
        if spectrum_data is None:
            return

        sub_window = self._viewer.mdiarea.addSubWindow(SpectraMdiSubWindow())

        # Connect add layer
        sub_window.toolbar.atn_create_layer.triggered.connect(
            self._create_layer)

        # Connect open model editor
        sub_window.toolbar.atn_model_editor.triggered.connect(
            self.viewer.model_editor_dock.show)
        sub_window.show()

        self.display_graph(spectrum_data, sub_window)

    def display_graph(self, spectrum_data, sub_window=None):
        if not isinstance(spectrum_data, LayerDataTreeItem):
            spectrum_data = self.model.create_layer(spectrum_data)

        if sub_window is None:
            sub_window = self._viewer.mdiarea.activeSubWindow()

        sub_window.graph.add_item(spectrum_data)

    def open_file(self, path):
        dialog = FileEditDialog(path)
        dialog.exec_()

        spec_data = read_data(path)
        name = path.split('/')[-1].split('.')[-2]
        self.add_data_set(spec_data, name)

    # ---- slot functions
    def _set_toolbar(self):
        sw = self.viewer.mdiarea.activeSubWindow()

        if sw is not None:
            tb = sw.toolbar
            self.viewer.set_toolbar(toolbar=tb)
        else:
            self.viewer.set_toolbar(hide_all=True)


def main():
    app = QtGui.QApplication(sys.argv)
    app_gui = Controller()
    app_gui.viewer.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()