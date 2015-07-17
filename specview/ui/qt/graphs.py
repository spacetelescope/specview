from itertools import cycle

from specview.external.qt import QtGui, QtCore
from specview.tools.graph_items import ExtendedFillBetweenItem
import pyqtgraph as pg

pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')
pg.setConfigOptions(antialias=False)


import numpy as np
# ignore divisions by zero
ignored_states = np.seterr(divide='ignore')

from specview.ui.items import SpectrumDataTreeItem, LayerDataTreeItem


class BaseGraph(pg.PlotWidget):
    sig_units_changed = QtCore.Signal()

    def __init__(self):
        super(BaseGraph, self).__init__()
        self.plot_window = self.getPlotItem()
        self.plot_window.setContentsMargins(5, 5, 5, 5)
        self.plot_window.showGrid(x=True, y=True)
        # Accept drag events
        self.setAcceptDrops(True)
        # Define layout
        # self.vb_layout = QtGui.QVBoxLayout()
        # self.setLayout(self.vb_layout)
        # Create main graphics layout widget
        # self.view_box = None
        # self.w = pg.PlotWidget()
        # self.vb_layout.addWidget(self.w)
        # Create roi container
        self._rois = []
        self._active_roi = None
        self._units = None

    @property
    def active_roi(self):
        return self._active_roi

    @property
    def rois(self):
        return self._rois

    def set_units(self, x=None, y=None, z=None):
        self._units = [u if u is not None else self._units[i]
                       for i, u in enumerate([x, y, z])]
        self.sig_units_changed.emit()

    def _set_active_roi(self):
        self._active_roi = self.sender()

    def dragEnterEvent(self, e):
        e.accept()

    def add_roi(self):
        view_range = self.viewRange()
        x_len = (view_range[0][1] - view_range[0][0]) * 0.5
        y_len = (view_range[1][1] - view_range[1][0]) * 0.5
        x_pos = x_len + view_range[0][0]
        y_pos = y_len + view_range[1][0]

        def remove():
            self.removeItem(roi)
            self._rois.remove(roi)

        roi = pg.RectROI([x_pos, y_pos], [x_len * 0.5, y_len * 0.5],
                         sideScalers=True, removable=True, pen='k')
        self._rois.append(roi)
        self.addItem(roi)

        # Connect the remove functionality
        roi.sigRemoveRequested.connect(remove)
        roi.sigRegionChangeFinished.connect(self._set_active_roi)

        # Let everyone know, ROI is ready for use.
        roi.sigRegionChangeFinished.emit(self)

    def get_roi_mask(self, layer_data_item):
        spec_data = layer_data_item.item

        x_data = spec_data.get_dispersion(self._units[0])
        y_data = spec_data.get_flux(self._units[1])

        mask_holder = []

        for roi in self._rois:
            roi_shape = roi.parentBounds()
            x1, y1, x2, y2 = roi_shape.getCoords()

            mask_holder.append((x_data.value >= x1) & (x_data.value <= x2) &
                               (y_data.value >= y1) & (y_data.value <= y2))

        mask = np.logical_not(reduce(np.logical_or, mask_holder))
        return mask

    def get_roi_data(self, layer_data_item):
        spec_data = layer_data_item.item

        x_data = spec_data.get_dispersion(self._units[0])
        y_data = spec_data.get_flux(self._units[1])

        if len(self._rois) == 0:
            print("No ROI's in plot; returning full arrays.")
            return x_data.value, y_data.value, x_data.unit, y_data.unit

        mask_holder = []

        for roi in self._rois:
            roi_shape = roi.parentBounds()
            x1, y1, x2, y2 = roi_shape.getCoords()

            mask_holder.append((x_data.value >= x1) & (x_data.value <= x2) &
                               (y_data.value >= y1) & (y_data.value <= y2))

        mask = np.logical_not(reduce(np.logical_or, mask_holder))
        return x_data.value[~mask], y_data.value[~mask], x_data.unit, \
               y_data.unit

    def get_active_roi_mask(self, x_data, y_data):
        roi_shape = self._active_roi.parentBounds()
        x1, y1, x2, y2 = roi_shape.getCoords()

        mask = ((x_data >= x1) & (x_data <= x2) &
                (y_data >= y1) & (y_data <= y2))

        mask = np.logical_not(mask)
        return mask


class SpectraGraph(BaseGraph):
    def __init__(self):
        super(SpectraGraph, self).__init__()
        self._plot_dict = {}
        self._active_plot = None
        self._active_item = None

        self.__colors = ['black', 'red', 'green', 'blue', 'yellow',
                         'cyan', 'magenta']
        self._icolors = cycle(self.__colors)

        # self.view_box = self.plot_window.getViewBox()

        self.sig_units_changed.connect(self.update_all)

        self.show_errors = True

    @property
    def active_item(self):
        return self._active_item

    @property
    def active_mask(self):
        spec_data = self.active_item.parent.item
        x_data, y_data = spec_data.get_dispersion(), spec_data.get_flux()

        return self.get_roi_mask(x_data, y_data)

    def _get_active_roi_data(self):
        spec_data = self.active_item.parent.item
        x_data, y_data = spec_data.x.data, spec_data.y.data
        mask = self.get_active_roi_mask(x_data, y_data)

        return x_data[~mask], y_data[~mask]

    @staticmethod
    def _get_roi_coords(roi):
        roi_shape = roi.parentBounds()
        x1, y1, x2, y2 = roi_shape.getCoords()
        return [x1, x2], [y1, y2]

    def update_all(self):
        for layer_data_item in self._plot_dict.keys():
            self.update_item(layer_data_item)

    def update_item(self, layer_data_item=None, style=None):
        if layer_data_item is None:
            layer_data_item = self._active_item

            if layer_data_item is None:
                return

        for plot, errs in self._plot_dict[layer_data_item]:
            print("[SpecView] Updating plot")
            color = plot.opts['pen']

            if style is None:
                if plot.opts['stepMode'] is True:
                    style = 'histogram'
                elif plot.opts['symbol'] is not None:
                    style = 'scatter'
                else:
                    style = 'line'

            spec_data = layer_data_item.item
            mask = layer_data_item.mask
            spec_x_array = spec_data.get_dispersion(self._units[0])[~mask]
            spec_y_array = spec_data.get_flux(self._units[1])[~mask]
            spec_y_err = spec_data.get_error(self._units[1])[~mask]

            x_data = spec_x_array.value if style != 'histogram' else np.append(
                spec_x_array.value, spec_x_array.value[-1])

            # This is a work around. If you don't turn off downsampling,
            # then the drastic change in units may cause *all* data points
            # to be deleted, and the autoscale will not be able to function.
            #  So first, turn off downsampling, plot data, autoscale,
            # then enable downsampling.
            self.plot_window.setDownsampling(ds=False, auto=False, mode='peak')

            self.plot_window.autoRange()

            plot.setData(x_data,
                         spec_y_array.value,
                         pen=color,
                         stepMode=style == 'histogram',
                         symbol='o' if style == 'scatter' else None)

            errs.setData(x=x_data, y=spec_y_array.value,
                         height=(1.0 / spec_y_err.value) ** 0.5,)
            #              pen=QtGui.QColor(0, 0, 0, 120))

            # errs.curves[0].setData(x_data,
            #                        spec_y_array.value + np.divide(1.0,
            #                                                spec_y_err.value)
            #                        ** 0.5 * 0.5)
            #
            # errs.curves[1].setData(x_data,
            #                 spec_y_array.value - np.divide(1.0,
            #                                                spec_y_err.value)
            #                        ** 0.5 * 0.5)

            if self.show_errors:
                errs.show()
            else:
                errs.hide()

            self.plot_window.autoRange()

            self.plot_window.setDownsampling(ds=True, auto=True, mode='peak')

            self.plot_window.setLabel('bottom', text='Dispersion [{}]'.format(
                                      spec_x_array.unit))
            self.plot_window.setLabel('left', text='Flux [{}]'.format(
                                      spec_y_array.unit))

    def add_item(self, layer_data_item, set_active=True, style='histogram',
                 color=None):
        color = next(self._icolors) if not color else color

        if layer_data_item not in self._plot_dict.keys():
            self._plot_dict[layer_data_item] = []

        if self._units is None:
            spec_data = layer_data_item.item
            self._units = [spec_data.get_dispersion().unit,
                           spec_data.get_flux().unit,
                           None]

        self._graph_data(layer_data_item, set_active, style, color)

    def remove_item(self, data_item):
        layer_data_items = []

        if isinstance(data_item, LayerDataTreeItem):
            layer_data_items.append(data_item)
        elif isinstance(data_item, SpectrumDataTreeItem):
            for layer in data_item.layers:
                if layer in self._plot_dict.keys():
                    layer_data_items.append(layer)
        else:
            return

        for layer_data_item in layer_data_items:
            for plot, errs in self._plot_dict[layer_data_item]:
                self.plot_window.removeItem(plot)
                self.plot_window.removeItem(errs)

        for layer_data_item in layer_data_items:
            del self._plot_dict[layer_data_item]

    def _graph_data(self, layer_data_item, set_active=True, style='histogram',
                    color=None):
        style = 'line'
        color = next(self._icolors) if color is None else color
        pen = QtGui.QPen(QtGui.QColor(color))

        spec_data = layer_data_item.item
        mask = layer_data_item.mask

        spec_x_array = spec_data.get_dispersion(self._units[0])[~mask]
        spec_y_array = spec_data.get_flux(self._units[1])[~mask]
        spec_y_err = spec_data.get_error(self._units[1])[~mask]

        x_data = spec_x_array.value if style != 'histogram' else np.append(
            spec_x_array.value, spec_x_array.value[-1])

        # plt_err_top = self.plot_window.plot(
        #     x_data,
        #     spec_y_array.value + np.divide(1.0, spec_y_err.value) ** 0.5 * 0.5)
        #
        # plt_err_btm = self.plot_window.plot(
        #     x_data,
        #     spec_y_array.value - np.divide(1.0, spec_y_err.value) ** 0.5 * 0.5)

        # plt_errs = ExtendedFillBetweenItem(window=self.plot_window,
        #                                    curve1=plt_err_top,
        #                                    curve2=plt_err_btm,
        #                                    brush=pg.mkColor(0, 0, 0, 60),
        #                                    pen=pg.mkColor(0, 0, 0, 60))

        plt_errs = pg.ErrorBarItem(x=x_data, y=spec_y_array.value,
                                   height=(1.0 / spec_y_err.value) ** 0.5,
                                   pen=pg.mkPen(0, 0, 0, 120),
                                   beam=(x_data[5] - x_data[4])*0.5)

        self.plot_window.addItem(plt_errs)

        plot = self.plot_window.plot(x_data,
                                     spec_y_array.value,
                                     pen=pen,
                                     stepMode=style == 'histogram',
                                     symbol='o' if style == 'scatter' else None)

        self.plot_window.setLabel('bottom',
                                  text='Dispersion [{}]'.format(
                                      spec_x_array.unit))
        self.plot_window.setLabel('left',
                                  text='Flux [{}]'.format(spec_y_array.unit))

        self.plot_window.setDownsampling(ds=True, auto=True, mode='peak')
        # self.plot_window.setClipToView(True)

        if plot not in self._plot_dict[layer_data_item]:
            self._plot_dict[layer_data_item].append([plot, plt_errs])

    def set_active(self, layer_data_item):
        self._active_plot = self._plot_dict[layer_data_item][-1]
        self._active_item = layer_data_item

    def select_active(self, layer_data_item):
        if layer_data_item not in self._plot_dict.keys():
            return

        plot = self._plot_dict[layer_data_item][-1]

        # if plot == self._active_plot:
        #     return
        # elif self._active_plot is not None:
        #     color = self._active_plot.opts['pen']
        #     # color.setAlpha(100)
        #     self._active_plot.setPen(color, width=2)
        #
        # color = plot.opts['pen']
        # # color.setAlpha(255)
        # plot.setPen(color, width=1)
        # self.set_active(layer_data_item)

    def set_visibility(self, layer_data_item, show, errors_only=False):
        for layers in self._plot_dict.values():
            for plot, errs in layers:
                if not show:
                    if not errors_only:
                        plot.hide()
                    errs.hide()
                else:
                    if not errors_only:
                        plot.show()
                    errs.show()


class ImageGraph(BaseGraph):
    def __init__(self):
        super(ImageGraph, self).__init__()
        # Add image window object
        data = np.random.normal(size=(100, 100))

        self.image_item = pg.ImageItem()
        self.set_image(data)

        # Create graph object
        self.view_box = self.w.addViewBox(lockAspect=True, row=1, col=0)

        # Add to viewbox
        g = pg.GridItem()
        self.addItem(g)
        self.addItem(self.image_item)

    def set_image(self, data):
        self.image_item.setImage(data)
