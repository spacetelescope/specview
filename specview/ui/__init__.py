import sys
from PyQt4 import QtGui, QtCore, Qt
from specview.qt import MainWindow
from specview.qt import ImageMdiSubWindow, SpectraMdiSubWindow
import specview
import numpy as np


class AppGUI(MainWindow):
    def __init__(self, model):
        super(AppGUI, self).__init__()
        self._model = model
        self.slot_menu_bar()
        self.slot_data_sets()

        for k, v in self._model.data_items.items():
            self.add_data_set(k)

        self.widget_console.localNamespace = {'model': self._model,
                                              'ui': self,
                                              'specview': specview,
                                              'np': np}

    def slot_menu_bar(self):
        self.menu_bar.docks_menu.addAction(
            self.dock_tree_view.toggleViewAction())
        self.menu_bar.docks_menu.addAction(
            self.dock_info_view.toggleViewAction())
        self.menu_bar.docks_menu.addAction(
            self.dock_console.toggleViewAction())

    def slot_data_sets(self):
        self.button_add_plot.clicked.connect(
            lambda: self.add_sub_window(
                self._model.data_items[
                    str(self.widget_tree_view_data.currentItem().text(0))
                ]
            )
        )

    def _viewer_drop_event(self, event):
        viewer, name = event
        viewer.add_plot(self._model.data_items[str(name)])

    def _open_file_dialog(self):
        fname = QtGui.QFileDialog.getOpenFileName(self, 'Open file')

    def add_sub_window(self, spectrum_data):
        sub_window = SpectraMdiSubWindow(self.mdiarea)
        sub_window.viewer.add_plot(spectrum_data)
        sub_window.viewer.receive_drop[tuple].connect(self._viewer_drop_event)
        sub_window.show()

    def add_data_set(self, name):
        new_item = QtGui.QTreeWidgetItem(self.widget_tree_view_data)
        new_item.setText(0, name)


def main(model):
    app = QtGui.QApplication(sys.argv)
    app_gui = AppGUI(model)
    app_gui.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    from specview.core.model import Model
    main(Model())