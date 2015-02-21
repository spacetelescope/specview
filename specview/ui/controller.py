import sys

from PyQt4 import QtGui
import numpy as np

from specview.ui.qt import MainWindow
from specview.ui.qt import ImageMdiSubWindow, SpectraMdiSubWindow
import specview
from specview.ui.qt import SpecViewItem, SpecViewModel


class Controller(object):
    def __init__(self):
        super(Controller, self).__init__()
        self._model = SpecViewModel()
        self._viewer = MainWindow()
        self._viewer.dock_data.wgt_data_tree.setModel(self._model)

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
    def _connect_mdiarea(self):
        self.viewer.mdiarea.subWindowActivated.connect(self._set_toolbar)

    def _connect_menu_bar(self):
        self._viewer.menu_bar.docks_menu.addAction(
            self._viewer.dock_data.toggleViewAction())
        self._viewer.menu_bar.docks_menu.addAction(
            self._viewer.dock_info.toggleViewAction())
        self._viewer.menu_bar.docks_menu.addAction(
            self._viewer.dock_console.toggleViewAction())

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

    def _open_file_dialog(self):
        fname = QtGui.QFileDialog.getOpenFileName(self, 'Open file')

    # ---- public functions
    def add_data_set(self, name, nddata, parent=None):
        ds_item = SpecViewItem(name, nddata)

        if parent is not None:
            parent.data_set_model.appendRow(ds_item)
        else:
            self.data_set_model.appendRow(ds_item)

    def add_sub_window(self, spectrum_data):
        sub_window = self._viewer.mdiarea.addSubWindow(SpectraMdiSubWindow())
        sub_window.graph.add_plot(spectrum_data)
        # sub_window.viewer.receive_drop[tuple].connect(self._viewer_drop_event)
        sub_window.show()

    def add_plot(self, spectrum_data):
        sub_window = self._viewer.mdiarea.activeSubWindow()
        sub_window.graph.add_plot(spectrum_data)
        sub_window.show()

    # ---- slot functions
    def _viewer_drop_event(self, event):
        viewer, name = event
        viewer.add_plot(self._model.data_items[str(name)])

    def _set_toolbar(self):
        sw = self.viewer.mdiarea.activeSubWindow()

        if sw is not None:
            self.viewer._hide_toolbars()
            tb = sw.toolbar
            self.viewer.addToolBar(tb)


def main():
    app = QtGui.QApplication(sys.argv)
    app_gui = Controller()
    app_gui.viewer.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()