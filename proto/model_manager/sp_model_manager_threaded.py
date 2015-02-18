from __future__ import division

import sys

import numpy as np
import astropy
from astropy.modeling import Parameter, Fittable1DModel, SummedCompositeModel
import astropy.modeling.functional_models as models

import sp_widget

from PyQt4.QtCore import *
from PyQt4.QtGui import *

# Main classes ------------------------------------------------

# Base class to be called by external apps.

class SpectralModelManager():
    def __init__(self, model=None):
        self._model = model
        if not self._model:
            self._model = []

    def buildSplitPanel(self, model=None):
        # override whatever model was passed to the constructor
        if model:
            self._model = model

        # When called the first time, build the two trees.
        # Subsequent calls must re-use the existing trees
        # so as to preserve user selections and such.
        if not hasattr(self, 'models_gui'):
            self.models_gui = sp_widget._SpectralModelsGUI(self._model)
            self._library_gui = sp_widget._SpectralLibraryGUI(self.models_gui)

        splitter = QSplitter();
        splitter.addWidget(self.models_gui.window)
        splitter.addWidget(self._library_gui.window)
        splitter.setStretchFactor(0, 1)
        return splitter

    @property
    def treeWidget(self):
        return self.models_gui.window.treeView

    @property
    def components(self):
        return self.models_gui.model.items

    def spectrum(self, wave):
        if len(self.components) > 0:
            sum_of_models = SummedCompositeModel(self.components)
            return sum_of_models(wave)
        else:
            return np.zeros(len(wave))

    def addModel(self, model):
        self.models_gui.updateModel(model)

    # Returns model selected in the library window.
    def getSelectedModel(self):
        return self._library_gui.getSelectedModel()

    # Returns model selected in the active components window.
    def selectedModel(self):
        return self.models_gui.getSelectedModel()

    def modifyModels(self, new_components):
        # This method must be called with a list of components that
        # matches the existing components in the model manager active
        # list. The method's purpose is to replace the parameter
        # values of each component with the values of the paired
        # component in the input list. Thus the lists have to match
        # perfectly.
        for i, c in enumerate(self.components):
            nc = new_components[i]
            c.parameters = nc.parameters

            # modify the tree model so the fit results
            # show immediately on the display.
            for j, value in enumerate(c.parameters):
                item = self.models_gui.model.item(i).child(j).child(0)
                item.setData("value: " + str(value), role=Qt.DisplayRole)


# Derived app class that builds the QApplication and runs it as a modal dialog.

class SpectralModelManagerApp(SpectralModelManager):
    def __init__(self, model=None):
        app = QApplication(sys.argv)

        splitter = self.buildSplitPanel(model)
        splitter.show()
        splitter.resize(550, 400)
        splitter.setSizes([350, 250])

        app.exec_()


# Functions and class that run the model manager in a separate
# thread so it can be called from an interactive session without
# blocking the interaction. Multiple models are supported; they
# are told apart by the 'name' parameter passed to the
# ModelManager constructor.
#
# Under MacOS with PyQt running in native Cocoa graphics mode,
# the code below will fail if run from a terminal window. It
# works when run from IPython though, or alternatively, when
# PyQt is built to run under a X11 server.

import pyqt_thread_helper
from pyqt_nonblock import QtNonblock

# GUI is a Singleton.
__dialog = None

# Selects threaded mode.
__threaded = False
__app = None


# Makes the GUI visible.
def display():
    global __dialog
    __dialog.emit(SIGNAL("show"))


# Adds a model manager to the GUI widget.
def add(manager, name=None):
    global __dialog
    __dialog.emit(SIGNAL("addManager"), manager.manager, name)


# Removes a model manager from the GUI widget.
def remove(name):
    global __dialog
    __dialog.emit(SIGNAL("removeManager"), name)


# Utility to generate text strings for the tabs in the
# tabbed pane, when the user fails to provide then.
__name_index = 0
def _getName(name):
    if not name or type(name) != type(" "):
        global __name_index
        __name_index += 1
        name = str(__name_index)
    return name


class _ModelManagerWidget(QTabWidget):
    def __init__(self, manager, name, parent=None, threaded=False):
        QTabWidget.__init__(self, parent)
        self._addManager(manager, name)
        self.setGeometry(100, 100, 650, 400)

        # I find this a more readable font.
        font = QFont(self.font())
        font.setPointSize(font.pointSize() + sp_widget.FONT_SIZE_INCREASE)
        self.setFont(font)

        # Because the widget and all its underlying PyQt stuff are running
        # in a separate thread, the only way to pass anything to the widget is via
        # Qt signal-slot events. Here we connect each supported signal to its
        # associated callback slot.
        self.connect(self, SIGNAL("addManager"), self._addManager)
        self.connect(self, SIGNAL("removeManager"), self._removeManager)
        self.connect(self, SIGNAL("show"), self._show)
        self.connect(self, SIGNAL('triggered()'), self.closeEvent)

        self.show()

    def _addManager(self, manager, name):
        widget = self._buildWidget(manager)

        name = _getName(name)
        if self.count() > 0:
            for i in range(0,self.count()):
                text = self.tabText(i)
                if text == name:
                    self.removeTab(i)
                    self.insertTab(i, widget, name)
                    self.setCurrentWidget(widget)
                    return

        self.addTab(widget, name)
        self.setCurrentWidget(widget)

    def _removeManager(self, name):
        name = _getName(name)
        if self.count() > 0:
            for i in range(0,self.count()):
                text = self.tabText(i)
                if text == name:
                    self.removeTab(i)
                    # to avoid a potential memory leak and completely get
                    # rid of the manager, at this point one should go deep
                    # into the View (ultimately, to the QApplication instance)
                    # to clear any references to the manager. We shouldn't be
                    # dealing with View code (this is the whole reason behind
                    # MVC), so lets leave it as is and see how it plays out
                    # (see comment below).
                    return

    def _buildWidget(self, manager):
        main_panel = manager.buildMainPanel()
        grid_layout = QGridLayout()
        grid_layout.addWidget(main_panel, 0, 0)

        exit_button = QPushButton('Close', self)
        exit_button.setFocusPolicy(Qt.NoFocus)
        self.connect(exit_button, SIGNAL('clicked()'), self._hide)
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(exit_button)
        grid_layout.addLayout(button_layout, 1, 0)

        result = QWidget()
        result.setLayout(grid_layout)
        return result

    def _hide(self):
        self.setVisible(False)

    def _show(self):
        self.setVisible(True)

    # Overrides the default behavior so as to ignore window closing
    # requests (such as from the platform-dependent red X button) and
    # respond instead by just making the window invisible. This in
    # fact renders the widget impossible to close except by terminating
    # the Python interactive session. This is required by the nature of
    # the underlying QApplication, when it is run in a secondary thread.
    # Under those conditions, only one QApplication can exist, and only
    # one can be created in any given Python session. A (desirable)
    # side effect is that the GUI contents, including user selections,
    # get preserved in between closed (invisible) and open (visible)
    # states. A (undesirable) side effect is that this might potentially
    # lead to memory leaks, since the GUI will prevent the garbage
    # collector to rid of unused model manager instances from the user's
    # interactive scope. In practice this might not be a problem unless
    # the user is dealing with thousands of manager instances, in which
    # case he/she shouldn't be using a GUI approach to begin with.
    def closeEvent(self, event):
        event.ignore()
        self._hide()


# Adds non-blocking behavior under ipython. This is done by
# just subclassing QtNonblock.
class _IPythonModelManagerWidget(_ModelManagerWidget, QtNonblock):
    def __init__(self, manager, name):
        super(_IPythonModelManagerWidget, self).__init__(manager, name)


def _runGUIInThread(manager, name):
    app = pyqt_thread_helper.getApplication()
    global __dialog
    if not __dialog:
        __dialog = _ModelManagerWidget(manager.manager, name)
    app.exec_()


def _runGUIDirectly(manager, name):
    global __dialog
    global __app
    if not __dialog:
        __app = QApplication([])
        __dialog = _ModelManagerWidget(manager.manager, name)
    return __dialog


def _runGUIInIPython(manager, name):
    global __dialog
    if not __dialog:
        __dialog = _IPythonModelManagerWidget.start_gui(manager.manager, name)


def _is_running_from_ipython():
    try:
        __IPYTHON__
        return True
    except NameError:
        return False


# The first time this function is called, it starts the thread to
# run the GUI, and passes to it the first instance of a model manager.
# Subsequent calls will just send signals to the GUI to add a new
# model manager and make the widget visible. Under ipython there is
# no need to start a separate thread though, since we use the qt_noblock
# mechanism to handle non-blocking behavior under the hood.
def _displayGUI(manager, name):
    global __dialog
    if not __dialog:
        global __threaded
        if __threaded:
            if not _is_running_from_ipython():
                pyqt_thread_helper.queueCommand(_runGUIInThread, arguments=[manager, name])
            else:
                _runGUIInIPython(manager, name)
        else:
            return _runGUIDirectly(manager, name)
    else:
        __dialog.emit(SIGNAL("addManager"), manager.manager, name)
        __dialog.emit(SIGNAL("show"))


# Main class. The user creates instances of this to manage a
# spectral model in each instance. For now, each instance starts
# with an empty model; the user then uses the GUI to add to and
# modify the model.

class ModelManager(object):
    def __init__(self, name=None, model=None):
        self.manager = SpectralModelManager(model)
        a = _displayGUI(self, name)

    # Use delegation to decouple the ModelManager API from
    # the GUI model manager API.

    def add(self, model):
        self.manager.addModel(model)

    @property
    def selected(self):
        return self.manager.selectedModel()

    @property
    def components(self):
        return self.manager.components

    def spectrum(self, wave):
        return self.manager.spectrum(wave)


if __name__ == "__main__":

    # valid formats for ModelManager constructor call.
    mm1 = ModelManager()
#    mm1 = ModelManager(model=[models.Gaussian1D(1.,1.,1.)])
#    mm1 = ModelManager('test1')
#    mm1 = ModelManager(model=[models.Gaussian1D(1.,1.,1.),models.Lorentz1D(1.,1.,1.)])
#    mm1 = ModelManager("test2", [models.Gaussian1D(1.,1.,1.),models.Lorentz1D(1.,1.,1.)])





