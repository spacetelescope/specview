from itertools import cycle

from PyQt4 import QtGui, QtCore
import pyqtgraph as pg
import numpy as np
from astropy.units import Unit

from specview.ui.qt.tree_items import SpectrumDataTreeItem, LayerDataTreeItem


COLORS = cycle(['g', 'r', 'c', 'm', 'y', 'w'])


class BaseGraph(QtGui.QWidget):
    sig_units_changed = QtCore.pyqtSignal()

    def __init__(self):
        super(BaseGraph, self).__init__()
        # Accept drag events
        self.setAcceptDrops(True)
        # Define layout
        self.vb_layout = QtGui.QVBoxLayout()
        self.setLayout(self.vb_layout)
        # Create main graphics layout widget
        self.view_box = None
        self.w = pg.GraphicsLayoutWidget()
        self.vb_layout.addWidget(self.w)
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
        view_range = self.view_box.viewRange()
        x_len = (view_range[0][1] - view_range[0][0]) * 0.5
        y_len = (view_range[1][1] - view_range[1][0]) * 0.5
        x_pos = x_len + view_range[0][0]
        y_pos = y_len + view_range[1][0]

        def remove():
            self.view_box.removeItem(roi)
            self._rois.remove(roi)

        roi = pg.RectROI([x_pos, y_pos], [x_len * 0.5, y_len * 0.5],
                         sideScalers=True, removable=True)
        self._rois.append(roi)
        # Assign roi
        self.view_box.addItem(roi)
        # Connect the remove functionality
        roi.sigRemoveRequested.connect(remove)
        roi.sigRegionChangeFinished.connect(self._set_active_roi)

    def get_roi_mask(self, x_data, y_data):
        mask_holder = []

        for roi in self._rois:
            roi_shape = roi.parentBounds()
            x1, y1, x2, y2 = roi_shape.getCoords()

            mask_holder.append((x_data >= x1) & (x_data <= x2) &
                               (y_data >= y1) & (y_data <= y2))

        mask = np.logical_not(reduce(np.logical_or, mask_holder))
        return mask

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

        self.plot_window = self.w.addPlot(row=1, col=0)
        self.plot_window.showGrid(x=True, y=True)
        self.view_box = self.plot_window.getViewBox()

        self.sig_units_changed.connect(self.update_all)

    @property
    def active_item(self):
        return self._active_item

    @property
    def active_mask(self):
        spec_data = self.active_item.parent.item
        x_data, y_data = spec_data.x.data, spec_data.y.data

        return self.get_roi_mask(x_data, y_data)

    def _get_active_roi_data(self):
        spec_data = self.active_item.parent.item
        x_data, y_data = spec_data.x.data, spec_data.y.data
        mask = self.get_active_roi_mask(x_data, y_data)

        return x_data[~mask], y_data[~mask]

    def _get_active_roi_coords(self):
        roi_shape = self._active_roi.parentBounds()
        x1, y1, x2, y2 = roi_shape.getCoords()
        return [x1, x2], [y1, y2]

    def update_all(self):
        layer_data_items = self._plot_dict.keys()

        for layer_data_item in layer_data_items:
            self.remove_item(layer_data_item)

        for layer_data_item in layer_data_items:
            self.add_item(layer_data_item)

    def add_item(self, layer_data_item, set_active=True, use_step=True):
        if layer_data_item in self._plot_dict.keys():
            self._plot_dict[layer_data_item].append(layer_data_item)
        else:
            self._plot_dict[layer_data_item] = []

        layer_data = layer_data_item.item

        if self._units is None:
            self._units = [layer_data.x.unit, layer_data.y.unit, None]

        self._graph_data(layer_data_item, set_active, use_step)

    def remove_item(self, data_item):
        # TODO: it's possible have multiple sub_windows try and delete the
        # same data. Need to implement a check to make sure the dictionary
        # still holds the data. May cause KeyError otherwise.
        layer_data_items = []

        if isinstance(data_item, LayerDataTreeItem):
            layer_data_items.append(data_item)
        elif isinstance(data_item, SpectrumDataTreeItem):
            for layer in data_item.layers:
                if layer in self._plot_dict.keys():
                    layer_data_items.append(layer)

        for layer_data_item in layer_data_items:
            for plot in self._plot_dict[layer_data_item]:
                self.plot_window.removeItem(plot)

        for layer_data_item in layer_data_items:
            del self._plot_dict[layer_data_item]

    def _graph_data(self, layer_data_item, set_active=True, use_step=True):
        spec_data = layer_data_item.item
        spec_x_array = spec_data.x.convert_unit_to(self._units[0])
        spec_y_array = spec_data.y.convert_unit_to(self._units[1])

        fin_pnt = spec_x_array.data[-1] - spec_x_array.data[-2] +\
                  spec_x_array.data[-1]

        x_data = np.append(spec_x_array.data, fin_pnt) if use_step else \
                           spec_x_array.data

        plot = pg.PlotDataItem(x_data,
                               spec_y_array.data,
                               pen=pg.mkPen(next(COLORS)),
                               clickable=True,
                               stepMode=use_step)

        self.plot_window.setLabel('bottom',
                                  text='Dispersion [{}]'.format(
                                      spec_x_array.unit),
                                  # units=spectrum_data.x.unit,
        )
        self.plot_window.setLabel('left',
                                  text='Flux [{}]'.format(
                                      spec_y_array.unit),
                                  # units=spectrum_data.y.unit,
        )

        self._plot_dict[layer_data_item].append(plot)
        self.plot_window.addItem(plot)

        if set_active:
            self.select_active(layer_data_item)

    def set_active(self, layer_data_item):
        self._active_plot = self._plot_dict[layer_data_item][-1]
        self._active_item = layer_data_item

        spectrum_data = layer_data_item.item

    def select_active(self, layer_data_item):
        if layer_data_item not in self._plot_dict.keys():
            return

        plot = self._plot_dict[layer_data_item][-1]

        if plot == self._active_plot:
            return
        elif self._active_plot is not None:
            color = self._active_plot.opts['pen'].color()
            color.setAlpha(100)
            self._active_plot.setPen(color, width=1)

        color = plot.opts['pen'].color()
        color.setAlpha(255)
        plot.setPen(color, width=2)
        self.set_active(layer_data_item)


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
        self.view_box.addItem(g)
        self.view_box.addItem(self.image_item)

    def set_image(self, data):
        self.image_item.setImage(data)
