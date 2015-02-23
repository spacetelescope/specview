from itertools import cycle

from PyQt4 import QtGui, QtCore
import pyqtgraph as pg
import numpy as np

from specview.analysis import model_fitting
from specview.core import SpectrumData


COLORS = cycle(['g', 'r', 'c', 'm', 'y', 'w'])


class BaseGraph(QtGui.QWidget):
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
        self._rois = list()

    @property
    def rois(self):
        return self._rois

    def layer_info(self):
        return self.get_roi_mask(), self._rois

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

    def get_roi_mask(self, x_data, y_data):
        mask_holder = []

        for roi in self._rois:
            roi_shape = roi.parentBounds()
            x1, y1, x2, y2 = roi_shape.getCoords()
            mask_holder.append((x_data >= x1) & (x_data <= x2) &
                               (y_data >= y1) & (y_data <= y2))

        return reduce(np.logical_or, mask_holder)

class SpectraGraph(BaseGraph):
    # Create drop signal
    receive_drop = QtCore.pyqtSignal(tuple)

    def __init__(self):
        super(SpectraGraph, self).__init__()
        self.plot_dict = {}
        self.active_plot = None
        # Add plot object
        self.plot_window = self.w.addPlot(row=1, col=0)
        self.plot_window.showGrid(x=True, y=True)
        self.view_box = self.plot_window.getViewBox()

    def add_plot(self, spec_data_item, name=None, mask=None, is_active=True,
                 use_step=True):
        print("adding plot")
        spec_data = spec_data_item.item
        fin_pnt = spec_data.x.data[-1] - spec_data.x.data[-2] +\
                  spec_data.x.data[-1]

        x_data = np.append(spec_data.x.data, fin_pnt) if use_step else \
                           spec_data.x.data

        plot = pg.PlotDataItem(x_data,
                            spec_data.y.data,
                            pen=pg.mkPen(next(COLORS)),
                            clickable=True,
                            stepMode=use_step)

        self.plot_window.addItem(plot)

        plot.sigClicked.connect(self.select_active)

        if name is None:
            name = "plot{}".format(len(self.plot_dict.keys()))

        self.plot_dict[plot] = spec_data_item

        if is_active:
            self.select_active(plot)

    def remove_plot(self, plot):
        pass

    def set_active(self, plot):
        self.active_plot = plot
        spectrum_data = self.plot_dict[plot].item

        self.plot_window.setLabel('bottom', text='',
                                  units=spectrum_data.x.unit)
        self.plot_window.setLabel('left', text='',
                                  units=spectrum_data.y.unit)

    def dropEvent(self, e):
        pass
        # self.receive_drop.emit((self, str(e.mimeData().text())))

    def select_active(self, plot):
        if plot == self.active_plot:
            return
        elif self.active_plot is not None:
            color = self.active_plot.opts['pen'].color()
            color.setAlpha(100)
            self.active_plot.setPen(color, width=1)

        color = plot.opts['pen'].color()
        color.setAlpha(255)
        plot.setPen(color)
        self.set_active(plot)

    def get_active_item(self):
        return self.plot_dict[self.active_plot]

    def get_active_roi_mask(self):
        spec_data = self.get_active_item().item
        x_data, y_data = spec_data.x.data, spec_data.y.data

        return self.get_roi_mask(x_data, y_data)


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
