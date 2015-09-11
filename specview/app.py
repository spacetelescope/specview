import sys
from cube_tools.core import SpectrumData

from .external.qt import QtGui
from .external.qt import QtCore

from .analysis import model_fitting
from .ui.items import LayerDataTreeItem
from .ui.viewer import MainWindow
from .ui.qt.dialogs import FileEditDialog
from .tools.preprocess import read_data
from .ui.models import DataTreeModel
from .ui.qt.proxies import DataProxyModel, LayerProxyModel


class Application(object):
    def __init__(self):
        self.viewer = MainWindow()
        self.viewer.show()
        self.model = DataTreeModel()

        self.data_proxy_model = DataProxyModel(self.viewer)
        self.data_proxy_model.setSourceModel(self.model)
        # self.data_proxy_model.setDynamicSortFilter(True)

        self.layer_proxy_model = LayerProxyModel(self.viewer)
        self.layer_proxy_model.setSourceModel(self.model)
        # self.layer_proxy_model.setDynamicSortFilter(True)

        self.viewer.set_view_models(self.model,
                                    self.data_proxy_model,
                                    self.layer_proxy_model)

        self.setup()
        self._connect_model_editor_dock()

    def setup(self):
        # When the open action is triggered, pop up file dialogue
        self.viewer.tool_bar.atn_open_data.triggered.connect(
            self.load_file)

        # Connect "Add new plot window" actions
        self.viewer.tool_bar.atn_new_plot.triggered.connect(
            self.create_plot_window)

        # When the checkbox next to a layer item is clicked, set the
        # visibility of that plot item
        self.model.sig_set_visibility.connect(self.viewer.set_layer_visibity)

    def load_file(self):
        fname = self.viewer.file_dialog.getOpenFileName(self.viewer, 'Open file')

        if not fname:
            return

        # dialog = FileEditDialog(fname)
        # dialog.exec_()
        #
        # if not dialog.result():
        #     return
        #
        # spec_data = read_data(fname, ext=dialog.ext, flux=dialog.flux,
        #                       dispersion=dialog.dispersion,
        #                       flux_unit=dialog.flux_unit,
        #                       dispersion_unit=dialog.disp_unit)

        spec_data = SpectrumData.read(fname)

        name = fname.split('/')[-1].split('.')[-2]
        self.add_data(spec_data, name)

    def add_data(self, nddata, name="Data", parent=None):
        return self.model.create_spec_data_item(nddata, name)

    def create_plot_window(self):
        if self.viewer.current_data_item is not None:
            layer_data_item = self.model.create_layer_item(
                self.viewer.current_data_item)
        else:
            layer_data_item = self.viewer.current_layer_item

        self.viewer.new_sub_window(layer_data_item)
        self.layer_proxy_model.invalidate()
        self.layer_proxy_model.sort(0)

    def _connect_model_editor_dock(self):
        model_selector = self.viewer.model_editor_dock.wgt_model_selector

        model_selector.activated.connect(lambda:
            self.model.create_fit_model(
                self.viewer.current_layer_item,
                self.viewer.selected_model))

        self.viewer.model_editor_dock.btn_perform_fit.clicked.connect(
            self._perform_fit)

    def _perform_fit(self):
        layer_data_item = self.viewer.current_layer_item

        fitter = model_fitting.get_fitter(self.viewer.selected_fitter)
        init_model = layer_data_item.model

        x, y = layer_data_item.item.x.data, layer_data_item.item.y.data

        fit_model = fitter(init_model, x, y)
        new_y = fit_model(x)

        # Update using model approach
        for model_idx in range(layer_data_item.rowCount()):
            model_data_item = layer_data_item.child(model_idx)

            for param_idx in range(model_data_item.rowCount()):
                parameter_data_item = model_data_item.child(param_idx, 1)

                if layer_data_item.rowCount() > 1:
                    value = fit_model[model_idx].parameters[param_idx]
                else:
                    value = fit_model.parameters[param_idx]
                parameter_data_item.setData(value)
                parameter_data_item.setText(str(value))

        fit_spec_data = SpectrumData(x=layer_data_item.item.x)
        fit_spec_data.set_y(new_y, wcs=layer_data_item.item.y.wcs,
                            unit=layer_data_item.item.y.unit)

        spec_data_item = self.add_data(fit_spec_data,
                                           name="Model Fit ({}: {})".format(
                                               layer_data_item.parent.text(),
                                               layer_data_item.text()))

        self.display_graph(spec_data_item)

    def display_graph(self, layer_data_item, sub_window=None, style='line'):
        if not isinstance(layer_data_item, LayerDataTreeItem):
            layer_data_item = self.model.create_layer_item(layer_data_item)

        if sub_window is None:
            sub_window = self.viewer.mdiarea.activeSubWindow()

        sub_window.graph.add_item(layer_data_item, style)


def run():
    app = QtGui.QApplication(sys.argv)
    win = Application()
    app.connect(app, QtCore.SIGNAL("lastWindowClosed()"),
                app, QtCore.SLOT("quit()"))
    app.exec_()


if __name__ == '__main__':
    run()

