import numpy as np
import pyqtgraph as pg
# from ...tools.graph_items import ExtendedFillBetweenItem


class SpectrumPlotContainer(object):
    def __init__(self, layer_data_item, units=None, style='line', visible=True,
                 plot_pen=None, err_pen=None):
        self._style = style
        self._plot_pen = plot_pen if plot_pen is not None else pg.mkPen()
        print(self._plot_pen)
        self._error_plot_pen = err_pen if err_pen is not None else pg.mkPen()

        self._visible = visible
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
        data = self.spec_data.get_dispersion(self._units[0])[self.filter_mask]

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
        self.plot_item.setData(x=self._x,
                               y=self._y,
                               pen=self._plot_pen,
                               stepMode=self._style == 'histogram',
                               symbol='o' if self._style == 'scatter' else
                               None)

        if 'IVAR' in (self.spec_data.meta.get('hdu_ids') or []):
            errs = (1 / self._err) ** 0.5
        else:
            errs = self._err ** 0.5

        if self._err is not None:
            self.error_plot_item.setData(
                x=self._x,
                y=self._y,
                height=errs,  # TODO: This is an assumption
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
