import sys

import numpy as np

from glue.qt.widgets import MplWidget
from glue.qt.glue_toolbar import GlueToolbar
from glue.qt.qtutil import get_icon, nonpartial
from glue.external.echo import callback_property, add_callback

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from astropy.modeling import Fittable1DModel, Parameter, models

from sp_model_manager import SpectralModelManager


def _build_axes(figure):

    # tight-layout clobbers manual positioning
    try:
        figure.set_tight_layout(False)
    except AttributeError:  # old MPL
        pass

    ax2 = figure.add_subplot(122)
    ax1 = figure.add_subplot(121, sharex=ax2)

    ax1.set_position([0.1, .35, .88, .6])
    ax2.set_position([0.1, .15, .88, .2])

    return ax1, ax2


class ParameterWidgets(object):

    def __init__(self, model, param):

        # param name
        self.label = QLabel(param)

        # value edit
        v = QDoubleValidator()
        e = QLineEdit()
        e.setValidator(v)
        e.setText(getattr(model, param))
        self.value = e

        # fixed checkbox
        w = QCheckBox()
        w.setChecked(model.fixed[param])
        self.fixed = w

        # lower limit
        e = QLineEdit()
        lims = model.limits[param]
        e.setText(str(lims[0]) if lims[0] is not None else '')
        self.lower = e

        # upper limit
        e = QLineEdit()
        lims = model.limits[param]
        e.setText(str(lims[1]) if lims[1] is not None else '')
        self.upper = e

        # tied
        e = QLineEdit()
        e.setText('')
        self.tied = e

    def set_model(self, *args):
        pass


class ModelSettingsDisplay(QWidget):

    def __init__(self, model, parent=None):
        super(QWidget, self).__init__(parent)
        self.model = model

        self.layout = QGridLayout()
        self.layout.setContentsMargins(2, 2, 2, 2)
        self.layout.setSpacing(4)

        self.setLayout(self.layout)

        self.layout.addWidget(QLabel("Value"), 0, 1)
        self.layout.addWidget(QLabel("Fixed"), 0, 2)
        self.layout.addWidget(QLabel("Lower Bound"), 0, 4)
        self.layout.addWidget(QLabel("Upper Bound"), 0, 5)
        self.layout.addWidget(QLabel("Tied"), 0, 6)


class Edit(object):

    def click(self, model, pos):
        raise NotImplementedError()

    def drag(self, model, a, b):
        raise NotImplementedError()

    def _set_as_y(self, model, attr, pos):
        model = model.copy()
        setattr(model, attr, pos.ydata)
        return model

    def _set_as_x(self, model, attr, pos):
        model = model.copy()
        setattr(model, attr, pos.ydata)
        return model

    def _change_as_dy(self, model, attr, a, b):
        model = model.copy()
        setattr(model, attr, getattr(model, attr) + (b.ydata - a.ydata))
        return model

    def _change_as_dx(self, model, attr, a, b):
        model = model.copy()
        setattr(model, attr, getattr(model, attr) + (b.xdata - a.xdata))
        return model


class AmplitudeEdit(object):

    def click(self, model, pos):
        return self._set_as_y(model, 'amplitude', pos)

    def drag(self, model, a, b):
        return self._change_as_dy(model, 'amplitude', a, b)


class MeanEdit(object):

    def click(self, model, pos):
        return self._set_as_x(model, 'mean', pos)

    def drag(self, model, a, b):
        return self._change_as_dx(model, 'mean', a, b)


class StddevEdit(object):

    def click(self, model, pos):
        result = model.copy()
        try:
            result.stddev = abs(pos.xdata - model.mean)
        except AttributeError:
            pass
        return result

    def drag(self, model, a, b):
        return self.click(model, b)


class LocationEdit(object):

    def click(self, model, pos):
        model = model.copy()
        try:
            model.amplitude = pos.ydata
        except AttributeError:
            pass
        try:
            model.mean = pos.xdata
        except AttributeError:
            pass
        return model

    def drag(self, model, a, b):
        dx = b.xdata - a.xdata
        dy = b.ydata - a.ydata
        result = model.copy()
        try:
            result.amplitude += dy
        except AttributeError:
            pass
        try:
            result.mean += dx
        except AttributeError:
            pass
        return result


class Trigger(object):

    def __init__(self):
        self.callbacks = []

    def connect(self, cb):
        self.callbacks.append(cb)

    def emit(self, *args, **kwargs):
        for c in self.callbacks:
            c(*args, **kwargs)


class DragTracker(object):

    def __init__(self, axes):
        self.DRAG_THRESH = 4

        self._drag = None
        self._drag_happened = False

        self.drag = Trigger()
        self.click = Trigger()
        self.drag_accepted = Trigger()

        self.axes = axes
        self.canvas = self.axes.figure.canvas
        self.canvas.mpl_connect('button_press_event', self.on_press)
        self.canvas.mpl_connect('button_release_event', self.on_release)
        self.canvas.mpl_connect('motion_notify_event', self.on_move)

    @property
    def _dragging(self):
        return self._drag is not None

    def _drag_dist(self, event):
        return max((abs(event.x - self._drag.x), abs(event.y - self._drag.y)))

    def _start_drag(self, e):
        self.canvas.widgetlock(self)
        self._drag = e

    def _reset_drag(self):
        if self.canvas.widgetlock.available(self):
            self.canvas.widgetlock.release(self)
        self._drag = None
        self._drag_happened = False

    def on_press(self, e):
        if not self.canvas.widgetlock.available(self):
            return

        if e.inaxes is not self.axes:
            self._reset_drag()
            return
        self._start_drag(e)

    def on_move(self, e):
        if not self._dragging:
            return

        if e.inaxes is not self.axes:
            self._reset_drag()
            return

        if self._drag_happened or self._drag_dist(e) > self.DRAG_THRESH:
            self._drag_happened = True
            self.drag.emit(self._drag, e)

    def on_release(self, e):
        if e.inaxes is not self.axes or not self._dragging:
            self._reset_drag()
            return

        if not self._drag_happened:
            self.click.emit(self._drag)
        else:
            self.drag_accepted.emit()

        self._reset_drag()


class ModelEventHandler(object):

    def __init__(self, axes, model):

        self.axes = axes

        self.reference_model = model
        self._current_model = model

        self._location = LocationEdit()
        self._stddev = StddevEdit()

        self.drag_tracker = DragTracker(self.axes)

        self.drag_tracker.drag.connect(self.on_drag)
        self.drag_tracker.drag_accepted.connect(self.on_accept)
        self.drag_tracker.click.connect(self.on_click)

    def _controller(self, event):
        if event.button == 1:
            return self._location
        return self._stddev

    @callback_property
    def model(self):
        return self._current_model

    @model.setter
    def model(self, value):
        self._current_model = value

    def on_drag(self, e1, e2):
        controller = self._controller(e1)
        self.model = controller.drag(self.reference_model,
                                     e1, e2)

    def on_accept(self):
        self._accept_model_update()

    def on_click(self, event):
        controller = self._controller(event)
        self.model = controller.click(self.reference_model, event)
        self._accept_model_update()

    def _accept_model_update(self):
        self.reference_model = self.model


class ModelBrowser(QObject):

    """
    A way to view, interact with, and fit models to a 1D spectrum
    """

    def __init__(self, x, y, dy, initial_models=None):

        QObject.__init__(self)
        
        self.x = x
        self.y = y
        self.dy = dy

        if initial_models is None:
            initial_models = [models.Const1D(0.0)]
        self.models = initial_models

        self.ui = ModelBrowserUI(self, self.models, self.x, self.y)
        self.plot, self.resid = _build_axes(self.ui.canvas.fig)
        self._draw(preserve_limits=False)

        self.mouse_handler = ModelEventHandler(self.plot, self.active_model)
        add_callback(self.mouse_handler, 'model', self.set_model)

        self.ui.fit.pressed.connect(nonpartial(self.fit))

        self._sync_model_list()

    @property
    def active_model(self):
        return self.models[self.active_row]

    @active_model.setter
    def active_model(self, value):
        self.models[self.active_row] = value

    @property
    def active_row(self):
        result = self.ui.manager.treeWidget.selectedIndexes()
        if len(result) < 1:
            return -1
        return result[0].row()

    def set_model(self, model):
        self.active_model = model
        self._draw()

    def add_model(self):
        component = self.ui.manager.getSelectedFromLibrary()

        row = self.active_row
        self.models.append(component)
        self.ui.manager.addComponent(component)
        self._sync_model_list(row)
        self._draw()

    def remove_model(self):
        row = self.active_row
        if row == 0:
            return  # don't delete the constant
        row = min((row, len(self.models) - 1))
        self.models.pop(row)
        self._sync_model_list(row)
        self._draw()

    def _sync_model_list(self, current_row=0):

        self.models = self.ui.manager.components

        self._draw()

        # for now, we just do a raw draw operation. Code
        # below might become necessary again in the future
        # when we re-implement the mouse point/drag
        # functionality.

#        self.ui.model_list.blockSignals(True)
#        self.ui.model_list.clear()
#
#        for m in self.models:
#            self.ui.model_list.addItem(str(m.__class__.__name__))
#
#        self.ui.model_list.blockSignals(False)
#        self.ui.model_list.setCurrentRow(current_row)

#        self.ui.model_list_list.treeView.blockSignals(True)
#        self.ui.model_list_list.treeView.clear()
#
#        for m in self.models:
#            self.ui.model_list_list.treeView.addItem(str(m.__class__.__name__))
#
#        self.ui.model_list_list.treeView.blockSignals(False)
#        self.ui.model_list_list.treeView.setCurrentRow(current_row)

    def _display_selected_model(self, current_row=0):
        level, index = self.ui.manager.models_gui.window.findTreeLevel()
        if level == 0:
            self._draw()

    def _draw(self, preserve_limits=True):
        if preserve_limits:
            xlim = self.plot.get_xlim()
            ylim = self.plot.get_ylim()

        self.plot.clear()
        self.resid.clear()

        x = self.x
        y = self.y

        m = self.ui.manager.spectrum(self.x)
        resid = y - m
        self.plot.plot(x, y, 'ko', x, m, 'k-')
        self.resid.plot(x, resid, 'ro')

        ma = self.active_model(self.x)
        self.plot.plot(x, ma, marker='None', color='#3875d7')

        if preserve_limits:
            self.plot.set_xlim(xlim)
            self.plot.set_ylim(ylim)

        self.plot.figure.canvas.draw()

    def show(self, raise_=True):
        self.ui.window.show()
        if raise_:
            self.ui.window.raise_()

    def fit(self):
        from astropy.modeling.fitting import LevMarLSQFitter

        components = self.ui.manager.components
        if len(components) > 0:
            model = superposition_model(*components)

            fitter = LevMarLSQFitter()
            model = fitter(model, self.x, self.y)
            self.models = model.terms()

            self.ui.manager.modifyModel(self.models)

            self._draw()


def superposition_model(*models):
    """
    An abomination to create a fittable superposition of astropy models
    """

    ps = []
    params = {}
    i = 0
    for m in models:
        for p in m.param_names:
            ps.append(Parameter())
            params['p_%i' % i] = ps[-1]
            i += 1

    def __init__(self, *args, **kwargs):
        for i, a in enumerate(args):
            kwargs['p_%i' % i] = a
        super(type(self), self).__init__(**kwargs)

    @staticmethod
    def eval(x, *args):
        result = 0
        i = 0
        for m in models:
            np = len(m.param_names)
            result += m.eval(x, *args[i:i + np])
            i += np
        return result

    @staticmethod
    def fit_deriv(x, *args):
        result = []
        i = 0
        for m in models:
            np = len(m.param_names)
            result += list(m.fit_deriv(x, *args[i:i + np]))
            i += np
        return result

    def terms(self):
        i = 0
        result = []
        for m in models:
            np = len(m.param_names)
            m = m.copy()
            for j in range(i, i + np):
                src = self.param_names[j]
                target = m.param_names[j - i]
                setattr(m, target, getattr(self, src))
            i += np
            result.append(m)
        return result

    params['__init__'] = __init__
    params['eval'] = eval
    params['fit_deriv'] = fit_deriv
    params['terms'] = terms

    result = type('Superposition', (Fittable1DModel,), params)

    args = sum((m.parameters.tolist() for m in models), [])
    return result(*args)


class ModelBrowserUI(object):

    def __init__(self, browser, model, x, y):
        # the GUI that enables selection and manipulation of
        # astropy spectral components is actually handled by
        # the SpectralModelManager class.
        self.manager = SpectralModelManager()
        # any change in the model manager should trigger
        # a refresh of the local spectral model. Component
        # selection should cause the component to be painted
        # in a distinct color.
        self.manager.changed.connect(browser._sync_model_list)
        self.manager.selected.connect(browser._display_selected_model)
        # the model manager needs to know the actual
        # data being plotted and fitted.
        self.manager.setArrays(x, y)

        model_list_gui = self.manager.buildMainPanel(model)
        model_list_gui.setStretchFactor(0,0)
        model_tree = self.manager.treeWidget

        win = QMainWindow()
        wid = QWidget()
        win.setCentralWidget(wid)
        l = QHBoxLayout()
        l.setSpacing(2)
        l.setContentsMargins(3, 3, 3, 3)
        wid.setLayout(l)

        widget = MplWidget()
        win.addToolBar(GlueToolbar(widget.canvas, win))
        l.addWidget(widget)

        right = QVBoxLayout()
        right.setSpacing(2)
        right.setContentsMargins(2, 0, 2, 0)

        right.addWidget(model_list_gui)

        buttons = QHBoxLayout()
        buttons.setSpacing(2)
        buttons.setContentsMargins(2, 0, 2, 0)

        right.addLayout(buttons)
        add = QPushButton(get_icon('glue_cross'), '')
        add.setToolTip('Add a spectral component')
        remove = QPushButton(get_icon('glue_delete'), '')
        remove.setToolTip('Remove the current spectral component')
        fit = QPushButton('Fit')
        fit.setToolTip("Fit model to spectrum")

        buttons.insertStretch(0, 1)
        buttons.addWidget(fit)
        l.addLayout(right)

        self.canvas = widget.canvas
        self.window = win
        self.model_list_gui = model_list_gui
        self.model_tree = model_tree
        self.remove = remove
        self.add = add
        self.fit = fit


# Test data

def test_data_1():
    # original
    x = np.linspace(-10, 10, 200)
    y = np.exp(-x ** 2) * 5
    y += np.exp(-(x - 3) ** 2 * 3) * 2
    y += 0.4
    return x,y

def test_data_2():
    # realistic values in Angstrom
    x = np.linspace(4000., 8000., 500)

    # realistic values in flam
    y =  np.exp(-((x-6000.)/200.)**2) * 5.E-14
    y += np.exp(-((x-6600.)/150.)**2) * 3.E-14
    y += 4.E-15

    return x,y

def test_data_3():
    # NGC3516
    import test_data
    x,y,e = test_data.get_data()
    return x,y

demo_data = {
    'original': test_data_1(),
    'realistic': test_data_2(),
    'NGC3516': test_data_3()
}



def demo(name):
    """
    Demo instructions (from original, demo changed since them)

    The list on the right of the plot shows the components of the model.
    Click on one to set it as the "active model", which can be tweaked by
    mouse interaction.

    Left click/dragging will adjust the amplitude and mean of the active model
    Right click/dragging will adjust the width

    You can add and delete models, as well as fit them
    (using the current values as a seed)

    Next steps:
    -----------

    Explore whether other mouse/keyboard gestures are better for tweaking parameters.
    Make the UI binding configurable
    Display and edit information about bounds, tied, fixed, etc
    Show and use errors
    """
    x, y = demo_data[name]

#    _models = [models.Const1D(0), models.Gaussian1D(3, 1, .3), models.Gaussian1D(3, 2, .3)]
#     _models = [models.Const1D(0)]
    _models = None

    mv = ModelBrowser(x, y, y * 0, _models)

    mv.show()

    from glue.qt import get_qapp
    get_qapp().exec_()

if __name__ == "__main__":
    demo(sys.argv[1])
