import sys

from PyQt4 import QtGui
import numpy as np

from specview.ui.qt import MainWindow
from specview.ui.qt import ImageMdiSubWindow, SpectraMdiSubWindow
import specview
from specview.ui.qt import SpectrumDataTreeItem, SpectrumDataTreeModel
from specview.io import read_data


class Controller(object):
    def __init__(self):
        super(Controller, self).__init__()
        self._model = SpectrumDataTreeModel()
        self._viewer = MainWindow()
        self._viewer.dock_data.wgt_data_tree.setModel(self._model)
        self._viewer.dock_model_editor.wgt_model_tree.setModel(self._model)

        self._connect_trees()
        self._connect_menu_bar()
        self._connect_data_dock()
        self._connect_mdiarea()

        self._viewer.dock_console.wgt_console.localNamespace = {
            'model': self._model,
            'ui': self,
            'specview': specview,
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
    def _connect_trees(self):
        self.viewer.dock_data.wgt_data_tree.clicked.connect(lambda:
            self.viewer.dock_model_editor.wgt_model_tree.set_root_index(
                self.viewer.dock_data.wgt_data_tree.current_item,
                self.viewer.dock_data.wgt_data_tree.currentIndex()
            )
        )

    def _connect_mdiarea(self):
        self.viewer.mdiarea.subWindowActivated.connect(self._set_toolbar)

    def _connect_menu_bar(self):
        self.viewer.menu_bar.atn_open.triggered.connect(self._open_file_dialog)

        self.viewer.menu_bar.docks_menu.addAction(
            self.viewer.dock_data.toggleViewAction())
        self.viewer.menu_bar.docks_menu.addAction(
            self.viewer.dock_info.toggleViewAction())
        self.viewer.menu_bar.docks_menu.addAction(
            self.viewer.dock_console.toggleViewAction())

    def _connect_data_dock(self):
        self._viewer.dock_data.btn_create_plot.clicked.connect(
            lambda: self.add_sub_window(
                self._viewer.dock_data.wgt_data_tree.current_item
            )
        )
        self._viewer.dock_data.btn_add_plot.clicked.connect(
            lambda: self.add_plot(
                self._viewer.dock_data.wgt_data_tree.current_item
            )
        )

    def _connect_model_add(self):
        pass

    def _open_file_dialog(self):
        fname = QtGui.QFileDialog.getOpenFileName(self.viewer, 'Open file')
        self.open_file(fname)

    # ---- public functions
    def add_data_set(self, nddata, name="Data", parent=None):
        self.model.create_data(nddata, name)

    def add_sub_window(self, spectrum_data, name=""):
        sub_window = self._viewer.mdiarea.addSubWindow(SpectraMdiSubWindow())
        sub_window.toolbar.atn_create_layer.triggered.connect(lambda:
            self.model.create_layer(
                sub_window.graph.get_active_item(),
                sub_window.graph.get_active_roi_mask()
            )
        )

        sub_window.graph.add_plot(spectrum_data)
        sub_window.setWindowTitle(name)
        sub_window.show()

    def add_plot(self, spectrum_data):
        sub_window = self._viewer.mdiarea.activeSubWindow()
        sub_window.graph.add_plot(spectrum_data)
        sub_window.show()

    def open_file(self, path):
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