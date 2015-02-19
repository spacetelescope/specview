from PyQt4 import QtGui, QtCore, Qt
import pyqtgraph as pg
import numpy as np
from toolbars import SpectraToolBar, ImageToolBar
from specview.analysis import fitting
from specview.core import SpectrumData
from itertools import cycle


COLORS = cycle(['g', 'r', 'c', 'm', 'y', 'w'])


class BaseViewer(QtGui.QWidget):
    def __init__(self):
        super(BaseViewer, self).__init__()
        # Accept drag events
        self.setAcceptDrops(True)
        # Define layout
        self.vb_layout = QtGui.QVBoxLayout()
        self.setLayout(self.vb_layout)
        # Create main graphics layout widget
        self.w = pg.GraphicsLayoutWidget()
        self.vb_layout.addWidget(self.w)

    def dragEnterEvent(self, e):
        e.accept()


class SpectraViewer(BaseViewer):
    # Create drop signal
    receive_drop = QtCore.pyqtSignal(tuple)

    def __init__(self):
        super(SpectraViewer, self).__init__()
        # Region list
        self.region_list = []
        # Add plot object
        self.plot_window = self.w.addPlot(row=1, col=0)
        self.plot_window.showGrid(x=True, y=True)
        self.view_box = self.plot_window.getViewBox()

        self.plot_dict = dict()
        self.active_plot = None

    def add_plot(self, spectrum_data, name=None, is_active=True):
        fin_pnt = spectrum_data.x.data[-1] - spectrum_data.x.data[-2] +\
                  spectrum_data.x.data[-1]
        plot = pg.PlotCurveItem(np.append(spectrum_data.x.data,
                                          fin_pnt),
                                spectrum_data.y.data,
                                pen=next(COLORS),
                                clickable=True,
                                stepMode=True)
        self.plot_window.addItem(plot)

        plot.sigClicked.connect(self.select_active)

        if name is None:
            name = "plot{}".format(len(self.plot_dict.keys()))

        self.plot_dict[plot] = spectrum_data

        if is_active:
            self.select_active(plot)

    def set_active(self, plot):
        self.active_plot = plot
        spectrum_data = self.plot_dict[plot]

        self.plot_window.setLabel('bottom', text='',
                                  units=spectrum_data.x.unit)
        self.plot_window.setLabel('left', text='',
                                  units=spectrum_data.y.unit)

    def dropEvent(self, e):
        self.receive_drop.emit((self, str(e.mimeData().text())))

    def select_active(self, plot):
        if plot == self.active_plot:
            return
        elif self.active_plot is not None:
            color = self.active_plot.opts['pen'].color()
            color.setAlpha(126)
            self.active_plot.setPen(color.getRgb(), width=1)

        color = plot.opts['pen'].color()
        color.setAlpha(255)
        plot.setPen(color, width=2)
        self.set_active(plot)

    def _add_region(self):
        region = pg.LinearRegionItem()
        region.setZValue(10)
        mn, mx = self.view_box.viewRange()[0]
        epsilon = (mx - mn) * 0.1
        region.setRegion([mn + epsilon, mn + epsilon * 2])
        self.plot_window.addItem(region, ignoreBounds=True)
        self.region_list.append(region)

    def _remove_region(self):
        self.plot_window.removeItem(self.region_list[-1])
        del self.region_list[-1]

    def _get_region_mask(self, x_data, y_data):
        mask_holder = []

        for region in self.region_list:
            x1, x2 = region.getRegion()
            mask_holder.append((x_data >= x1) & (x_data <= x2))

        return reduce(np.logical_or, mask_holder)

    def _fit_region(self):
        spectrum_data = self.plot_dict[self.active_plot]
        y_data = spectrum_data.y.data
        x_data = spectrum_data.x.data

        mask = self._get_region_mask(x_data, y_data)
        print(mask)

        coeff, x, y = fitting.gaussian(x_data[mask], y_data[mask])
        spectrum_data = SpectrumData()
        spectrum_data.set_x(x, unit='micron')
        spectrum_data.set_y(y, unit='erg/s')
        self.add_plot(spectrum_data, is_active=False)


class ImageViewer(BaseViewer):
    def __init__(self):
        super(ImageViewer, self).__init__()
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
