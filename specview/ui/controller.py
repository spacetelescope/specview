import numpy as np

from specview.core.history import history
from specview.ui.viewer import MainWindow
from specview.ui.model import SpectrumDataTreeModel
from specview.ui.qt.tree_items import LayerDataTreeItem
from specview.ui.qt.subwindows import SpectraMdiSubWindow
from specview.analysis.model_fitting import get_fitter
from specview.core.data_objects import SpectrumData
from specview.tools.preprocess import read_data
from specview.ui.qt.dialogs import FileEditDialog
from specview.tools.plugins import plugins
from specview.analysis.statistics import stats, eq_width, extract


class Controller(object):
    def __init__(self):
        super(Controller, self).__init__()
        self._model = SpectrumDataTreeModel()
        self._viewer = MainWindow(show_console=self._kernel['client'] is not None)
        self._viewer.data_dock.wgt_data_tree.setModel(self._model)
        self._viewer.model_editor_dock.wgt_model_tree.setModel(self._model)

        self.__connect_trees()
        self.__connect_menu_bar()
        self.__connect_data_dock()
        self.__connect_mdiarea()
        self.__connect_model_editor_dock()
        self.__connect_active_data()
        self.__connect_console()

        # Load in plugins
        self.ops = plugins({'controller': self})

        # Expose the data, results from internal calculations.
        self.dc = self._model.dc
        self.fc = self._model.fc
        self.history = history

        # This should definitely be formalized, but for the sake of the
        # demo, it's good enough
        self._main_name_space = {'np': np,
                                 'add_data_set': self.add_data_set,
                                 'history': self.history
        }
        self._main_name_space.update(self.ops.namespace)
        self._update_namespace()

    # -- properties
    @property
    def viewer(self):
        return self._viewer

    @property
    def model(self):
        return self._model

    # -- private functions
    def __connect_active_data(self):
        self.viewer.data_dock.wgt_data_tree.clicked.connect(
            self.update_active_plots)

    def __connect_model_editor_dock(self):
        model_selector = self.viewer.model_editor_dock.wgt_model_selector
        model_selector.activated.connect(self._create_model)

        self.viewer.model_editor_dock.btn_perform_fit.clicked.connect(
            self._perform_fit)

    def __connect_trees(self):
        self.viewer.data_dock.wgt_data_tree.sig_current_changed.connect(
            self.viewer.model_editor_dock.wgt_model_tree.set_root_index)

    def __connect_mdiarea(self):
        self.viewer.mdiarea.subWindowActivated.connect(self._set_toolbar)

    def __connect_menu_bar(self):
        self.viewer.menu_bar.atn_open.triggered.connect(self._open_file_dialog)
        self.viewer.menu_bar.atn_exit.triggered.connect(self.viewer.close)

    def __connect_data_dock(self):
        self.viewer.data_dock.btn_create_plot.clicked.connect(
            self._create_display)
        self.viewer.data_dock.btn_add_plot.clicked.connect(self._display_item)
        self.viewer.data_dock.btn_remove_plot.clicked.connect(
            self._remove_display_item)

    def __connect_console(self):
        self.model.itemChanged.connect(self._update_namespace)
        self.model.sig_added_item.connect(self._update_namespace)
        self.model.sig_removed_item.connect(self._update_namespace)

        self.viewer.console_dock.wgt_console.kernel_client = self._kernel['client']
        self.viewer.console_dock.wgt_console.shell = self._kernel['shell']

    # -- protected functions
    def _create_display(self):
        item = self.viewer.data_dock.wgt_data_tree.current_item

        if item is not None:
            self.create_display(item)

    def _display_item(self):
        item = self.viewer.data_dock.wgt_data_tree.current_item

        if item is not None:
            self.display_graph(item)

    def _remove_display_item(self):
        items = self.viewer.data_dock.wgt_data_tree.selected_items

        if items is not None:
            for item in [x for x in items if x is not None]:
                self.remove_graph(item)

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
        layer_data_item = self.viewer.data_dock.wgt_data_tree.current_item

        if not isinstance(layer_data_item, LayerDataTreeItem):
            return

        fitter_name = self.viewer.model_editor_dock.wgt_fit_selector.currentText()
        fitter = get_fitter(str(fitter_name))
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

        spec_data_item = self.add_data_set(fit_spec_data,
                                           name="Model Fit ({}: {})".format(
                                               layer_data_item.parent.text(),
                                               layer_data_item.text()))

        self.display_graph(spec_data_item)

    def _open_file_dialog(self):
        fname = self.viewer.file_dialog.getOpenFileName(self.viewer,
                                                        'Open file')
        self.open_file(fname)

    # -- public functions
    def update_active_plots(self, *args):
        item = self.viewer.data_dock.wgt_data_tree.current_item

        if isinstance(item, LayerDataTreeItem):
            for sub_window in self.viewer.mdiarea.subWindowList():
                sub_window.graph.select_active(item)

    def add_data_set(self, nddata, name="Data", parent=None):
        """Add a dataset to the list.

        Parameters
        ----------
        nddata: SpectrumData
            The data to add.
        """
        return self.model.create_data_item(nddata, name)

    def create_display(self, spectrum_data):
        """Create a plot display with the given data.

        Parameters
        ----------
        spectrum_data: SpectrumData
            The data to display
        """
        if spectrum_data is None:
            return

        sub_window = self._viewer.mdiarea.addSubWindow(SpectraMdiSubWindow())
        sub_window.show()

        # Connect add layer
        sub_window.toolbar.atn_create_layer.triggered.connect(
            self._create_layer)

        # Connect open model editor
        sub_window.toolbar.atn_model_editor.triggered.connect(
            self.viewer.model_editor_dock.show)

        # Connect measurement action
        sub_window.toolbar.atn_measure.triggered.connect(lambda:
            self.get_measurements(sub_window))

        # Connect equivalent width action
        sub_window.toolbar.atn_equiv_width.triggered.connect(lambda:
            self.get_equivalent_widths(sub_window))

        # Connect remove item
        self.model.sig_removed_item.connect(sub_window.graph.remove_item)

        self.display_graph(spectrum_data, sub_window)

    def display_graph(self, layer_data_item, sub_window=None, set_active=True,
                      style='histogram'):
        if not isinstance(layer_data_item, LayerDataTreeItem):
            layer_data_item = self.model.create_layer(layer_data_item)

        if sub_window is None:
            sub_window = self.viewer.mdiarea.activeSubWindow()

        sub_window.graph.add_item(layer_data_item, set_active, style)

    def remove_graph(self, layer_data_item, sub_window=None):
        if not isinstance(layer_data_item, LayerDataTreeItem):
            return

        if sub_window is None:
            sub_window = self.viewer.mdiarea.activeSubWindow()

        sub_window.graph.remove_item(layer_data_item)

    def get_measurements(self, sub_window):
        roi = sub_window.graph._active_roi

        if roi is None:
            return

        x_range, y_range = sub_window.graph._get_roi_coords(roi)
        active_item = sub_window.graph.active_item
        active_data = active_item.item

        region = extract(active_data, x_range)
        stat = stats(region)

        self.viewer.measurement_dock.set_labels(stat,
                                         data_name=active_item.parent.text(),
                                         layer_name=active_item.text())
        self.viewer.measurement_dock.show()

    def get_equivalent_widths(self, sub_window):
        # Get ROI stats
        stat_list = []
        x_rois = []
        for roi in sub_window.graph.rois[-2:]:
            if roi is None:
                continue

            x_range, y_range = sub_window.graph._get_roi_coords(roi)
            active_item = sub_window.graph.active_item
            active_data = active_item.item

            region = extract(active_data, x_range)
            stat_list.append(stats(region))
            x_rois.append(x_range)

        # Determine feature bounds
        if x_rois[0][1] < x_rois[1][0]:
            feature_roi = (x_rois[0][1], x_rois[1][0])
        else:
            feature_roi = (x_rois[1][1], x_rois[0][0])

        # Get the equivalent width
        self.ops.eq_width(stat_list[0], stat_list[1], extract(active_data, feature_roi))

    def open_file(self, path):
        if not path:
            return

        dialog = FileEditDialog(path)
        dialog.exec_()

        if not dialog.result():
            return

        spec_data = read_data(path, ext=dialog.ext, flux=dialog.flux,
                              dispersion=dialog.dispersion,
                              flux_unit=dialog.flux_unit,
                              dispersion_unit=dialog.disp_unit)

        name = path.split('/')[-1].split('.')[-2]
        self.add_data_set(spec_data, name)

    # -- slot functions
    def _set_toolbar(self):
        sw = self.viewer.mdiarea.activeSubWindow()

        if sw is not None:
            tb = sw.toolbar
            self.viewer.set_toolbar(toolbar=tb)
        else:
            self.viewer.set_toolbar(hide_all=True)

    def _update_namespace(self, item=None):
        if self.viewer.console_dock.wgt_console.shell is not None:
            local_namespace = self._main_name_space
            local_namespace.update(dict(self.model.dc))
            self.viewer.console_dock.wgt_console.shell.push(local_namespace)
