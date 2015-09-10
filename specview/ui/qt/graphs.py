from __future__ import print_function
from collections import namedtuple

from itertools import cycle
import pyqtgraph as pg
import numpy as np
# ignore divisions by zero
ignored_states = np.seterr(divide='ignore')
import astropy.constants as const
import astropy.units as u

from ...external.qt import QtGui, QtCore
from ...tools.graph_items import ExtendedFillBetweenItem

pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')
pg.setConfigOptions(antialias=False)

from specview.ui.items import SpectrumDataTreeItem, LayerDataTreeItem


class BaseGraph(pg.PlotWidget):
    sig_units_changed = QtCore.Signal()

    def __init__(self, *args, **kwargs):
        super(BaseGraph, self).__init__(*args, **kwargs)
        # Accept drag events
        self.setAcceptDrops(True)
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
        self.plot_window.autoRange()
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

        # mask = np.logical_not(reduce(np.logical_or, mask_holder))
        mask = reduce(np.logical_or, mask_holder)
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
        self._top_axis = DynamicAxisItem(self, orientation='top')
        super(SpectraGraph, self).__init__(axisItems={'top': self._top_axis})
        self.plot_window = self.getPlotItem()
        self._top_axis.linkToView(self.plot_window.getViewBox())
        self.plot_window.setContentsMargins(5, 5, 5, 5)
        self.plot_window.showGrid(x=True, y=True)
        self.plot_window.showAxis('top', True)
        self.plot_window.setDownsampling(ds=True, auto=True, mode='peak')

        # Define the display of the top axis
        self._top_axis = self.plot_window.getAxis('top')

        self._plot_containers = []
        self.__colors = ['black', 'red', 'green', 'blue', 'yellow', 'cyan',
                         'magenta']
        self._icolors = cycle(self.__colors)
        self._global_visibility = {'plot': True, 'errors': True}

        self.sig_units_changed.connect(self.update)

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

    def update(self, layer_data_item=None):
        for container in self._plot_containers:
            if container.layer_data_item == layer_data_item or \
                    layer_data_item is None:
                container.set_units(*self._units)
                container.update()

        self.set_labels()

    def add_item(self, layer_data_item, style='line', pen=None):
        pen = pg.mkPen(next(self._icolors)) if pen is None else pg.mkPen(**pen)

        spec_plot_container = SpectrumPlotContainer(layer_data_item,
                                                    plot_pen=pen,
                                                    style=style)
        spec_plot_container.set_visibility(self._global_visibility['plot'])
        spec_plot_container.set_error_visibility(self._global_visibility[
                                                  'errors'])

        self._plot_containers.append(spec_plot_container)
        self.plot_window.addItem(spec_plot_container.plot_item)
        self.plot_window.addItem(spec_plot_container.error_plot_item)

        if self._units is None:
            spec_data = layer_data_item.item
            self._units = [spec_data.get_dispersion().unit,
                           spec_data.get_flux().unit,
                           None]

        self.set_labels()

    def remove_item(self, layer_data_item):
        for container in self._plot_containers:
            if container.layer_data_item == layer_data_item:
                self.plot_window.removeItem(container.plot_item)
                self.plot_window.removeItem(container.error_plot_item)
                self._plot_containers.remove(container)

    def set_labels(self):
        self.plot_window.setLabel('bottom',
                                  text='Wavelength [{}]'.format(
                                      self._units[0]))
        self.plot_window.setLabel('left',
                                  text='Flux [{}]'.format(self._units[1]))

    def set_visibility(self, layer_data_item=None, show=True):
        if layer_data_item is None:
            self._global_visibility['plot'] = show

        for container in self._plot_containers:
            if container.layer_data_item == layer_data_item or \
                    layer_data_item is None:
                container.set_visibility(show)

    def set_error_visibility(self, layer_data_item=None, show=True):
        if layer_data_item is None:
            self._global_visibility['errors'] = show

        for container in self._plot_containers:
            if container.layer_data_item == layer_data_item or \
                    layer_data_item is None:
                container.set_error_visibility(show)


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


class DynamicAxisItem(pg.AxisItem):
    def __init__(self, graph, *args, **kwargs):
        super(DynamicAxisItem, self).__init__(*args, **kwargs)
        self._allowed_modes = ['redshift', 'velocity', 'channel']
        self._graph = graph
        self._data = None
        self._redshift = 0.0
        self._ref_wavelength = 0.0
        self._mode = "redshift"
        self._xdata = None
        self.setGrid(False)

    def set_mode(self, mode, ref_wavelength=None, redshift=None):
        if mode in [0, 1, 2]:
            self._mode = self._allowed_modes[mode]
        elif mode in self._allowed_modes:
            self._mode = mode
        else:
            return

        if ref_wavelength is not None:
            self._ref_wavelength = ref_wavelength

        if redshift is not None:
            self._redshift = redshift

        if self._mode == 'channel':
            self._xdata = self._graph._plot_dict.keys()[0].item.get_dispersion(
                self._graph._units[0]).value
            self.setTicks([
                [(v, str(i)) for i, v in enumerate(self._xdata)][::len(self._xdata)/10]
            ])
        else:
            self.setTicks(None)

        if self._mode in ['channel', 'velocity']:
            self.enableAutoSIPrefix(False)
        else:
            self.enableAutoSIPrefix(True)

        self.update()
        self.updateAutoSIPrefix()

    @property
    def mode(self):
        return self._mode

    def generateDrawSpecs(self, p):
        if self._mode == 'channel':
            mn, mx = self.range[0], self.range[1]
            self.enableAutoSIPrefix(False)
            self.setLabel("Channel", None, None)
            data = self._xdata[(self._xdata > mn) & (self._xdata <
                                                              mx)]
            self.setTicks([
                [(v, str(i)) for i, v in enumerate(data)][::len(
                    data)/10]
            ])
        return super(DynamicAxisItem, self).generateDrawSpecs(p)

    def tickStrings(self, values, scale, spacing):
        spatial_unit = self._graph._units[0] if self._graph._units is not \
                                                None else u.Unit('')
        if self._mode == 'redshift':
            self.setLabel('Redshifted Wavelength [{}]'.format(spatial_unit))
            return [v/(1 + self._redshift)*scale for v in values]
        elif self._mode == 'velocity':
            self.enableAutoSIPrefix(False)
            # self.setScale(1.0)
            self.setLabel("Velocity [km/s]", None, None)
            c = const.c.to('{}/s'.format(spatial_unit))
            waves = u.Quantity(np.array(values), spatial_unit)
            ref_wave = u.Quantity(self._ref_wavelength, spatial_unit)
            v = (waves - ref_wave) / waves * c
            return v.to('km/s').value
        elif self._mode == 'channel':
            return super(DynamicAxisItem, self).tickStrings(values, scale,
                                                            spacing)
        else:
            print("[ERROR] Not such mode {}".format(self._mode))


class SpectrumPlotContainer(object):
    def __init__(self, layer_data_item, units=None, style='line', visible=True,
                 plot_pen=None, err_pen=None):
        self._style = style
        self._plot_pen = plot_pen if plot_pen is not None else pg.mkPen()
        self._error_plot_pen = err_pen if err_pen is not None else pg.mkPen()

        self._visible = True
        self._error_visible = True
        self._units = units

        self.layer_data_item = layer_data_item

        self.spec_data = layer_data_item.item
        self.filter_mask = layer_data_item.filter_mask

        if self._units is None:
            self._units = [self.spec_data.get_dispersion().unit,
                           self.spec_data.get_flux().unit,
                           None]

        self.error_plot_item = pg.ErrorBarItem()
        self.plot_item = pg.PlotDataItem()
        self.update()

    @property
    def _x(self):
        data = self.spec_data.get_dispersion(self._units[0])[
            self.filter_mask]

        if self._style == 'histogram':
            return np.append(data.value, data.value[-1])

        return data.value

    @property
    def _y(self):
        return self.spec_data.get_flux(self._units[1])[self.filter_mask].value

    @property
    def _err(self):
        if self.spec_data.error is not None:
            return self.spec_data.get_error(self._units[1])[
                self.filter_mask].value

        return None

    def update(self):
        # self.plot_window.autoRange()

        self.plot_item.setData(x=self._x,
                               y=self._y,
                               pen=self._plot_pen,
                               stepMode=self._style == 'histogram',
                               symbol='o' if self._style == 'scatter' else
                               None)

        if self._err is not None:
            self.error_plot_item.setData(
                x=self._x,
                y=self._y,
                height=(1.0 / self._err) ** 0.5,
                pen=pg.mkPen(0, 0, 0, 60),
                beam=(self._x[5] - self._x[4])*0.5)

        # plt_err_top = pg.PlotDataItem(x=self._x,
        #                               y=self._y + np.divide(1.0, self._y) **
        #                               0.5 * 0.5)
        #
        # plt_err_btm = pg.PlotDataItem(x=self._x,
        #                               y=self._y - np.divide(1.0, self._y) **
        #                               0.5 * 0.5)
        #
        # self.error_plot_item = pg.FillBetweenItem(curve1=plt_err_top,
        #                                           curve2=plt_err_btm,)

    def set_units(self, x=None, y=None, z=None):
        self._units = [x, y, z]

    def set_visibility(self, visible):
        self._visible = visible

        if self._visible:
            self.plot_item.show()

            if self._error_visible:
                self.error_plot_item.show()
        else:
            self.plot_item.hide()
            self.error_plot_item.hide()

    def set_error_visibility(self, visible):
        self._error_visible = visible

        if not self._visible:
            return

        if self._error_visible:
            self.error_plot_item.show()
        else:
            self.error_plot_item.hide()

    def set_data_item(self, layer_data_item):
        self.layer_data_item = layer_data_item

    def set_plot_pen(self, *args, **kwargs):
        self._plot_pen = pg.mkPen(*args, **kwargs)
        self.update()

    def set_error_pen(self, *args, **kwargs):
        self._error_plot_pen = pg.mkPen(*args, **kwargs)
        self.update()


