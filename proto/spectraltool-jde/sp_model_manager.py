from __future__ import division

import sys
import warnings

from pyqt_nonblock import pyqtapplication

import models_registry
import sp_widget
from sp_widget import SpectralModelManager, SignalModelChanged

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from specview_signals import *
from spectrum_data import SpectrumData

# Derived app class that builds the QApplication and runs it as a modal dialog.

class SpectralModelManagerApp(SpectralModelManager):
    def __init__(self, model=None):

        super(SpectralModelManagerApp, self).__init__()

        app = QApplication(sys.argv)

        self.x = None
        self.y = None

        mainPanel = self.buildMainPanel(model)
        mainPanel.show()
        mainPanel.resize(550, 400)
        mainPanel.setSizes([350, 250])

        app.exec_()


# Functions and classes that run the model manager in non-block
# mode so it can be called from an interactive session without
# blocking the interaction. Multiple models are supported; they
# are told apart by the 'name' parameter passed to the
# ModelManager constructor.

# GUI is a Singleton. Note that the QApplication instance must be
# treated as as Singleton as well. It must be retained as a global
# reference in the module. Otherwise the GUI won't stay for long
# on screen.
__dialog = None
__app = None


def display():
    ''' Makes the GUI visible.

    This is to be used after the GUI disappears from screen
    when the 'Close' button is clicked.

    '''
    global __dialog
    __dialog.setVisible(True)


def remove(name):
    ''' Removes a model manager tab from the GUI widget.

    Note that the model manager instance continues to be valid after
    this function is called. It is just the tabbed panel in the GUI
    widget that gets removed. The model manager instance can be added
    back again via function 'add'.

    Parameters
    ----------
    name: str
      The name string in the tab that will be removed.

    '''
    global __dialog
    __dialog._removeManager(name)


def add(manager, name=None):
    ''' Adds a model manager tab to the GUI widget.

    Parameters
    ----------
    manager: ModelManager instance
      the model manager to be added to the GUI
    name: str, optional
      The name string that goes in the tab that will be added. If no
      name is provided, the function will pick the next unused string
      in the sequence '1', '2', '3', ....

    '''
    global __dialog
    __dialog._addManager(manager.manager, name)


def refresh():
    ''' Forces an update of the GUI to the current
        state of the ModelManager instances.

        This is the programmatic way of performing
        the same actions triggered by the 'Refresh'
        button.
    '''
    global __dialog
    __dialog._refresh()


# Utility to generate text strings for the tabs in the
# tabbed pane, when the user fails to provide then.
__name_index = 0
def _getName(name):
    if not name or type(name) != type(" "):
        global __name_index
        __name_index += 1
        name = str(__name_index)
    return name


# This class basically provides a stand-alone tabbed widget that
# contains multiple instances of the main panel created by
# SpectralModelManager. Each tab holds the rendering created by
# SpectralModelManager for an individual instance of ModelManager.
#
# The tabbed widget also supports some functionality that make sense
# only when all this stuff is run in interactive mode from the
# command line, such as 'Close' and 'Refresh' buttons.
#
class _ModelManagerWidget(QTabWidget):
    def __init__(self, manager, name, parent=None, threaded=False):
        QTabWidget.__init__(self, parent)
        self._addManager(manager, name)
        self.setGeometry(100, 100, 650, 400)

        # I find this a more readable font.
        font = QFont(self.font())
        font.setPointSize(font.pointSize() + sp_widget.FONT_SIZE_INCREASE)
        self.setFont(font)
        QToolTip.setFont(font)

        self.setVisible(True)

    def _addManager(self, manager, name):
        widget = self._buildWidget(manager)

        name = _getName(name)
        manager.name = name
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

        button_layout = QHBoxLayout()
        button_layout.addStretch()

        refresh_button = QPushButton('Refresh', self)
        refresh_button.setFocusPolicy(Qt.NoFocus)
        refresh_button.setToolTip('Forces window contents to match internal state of ModelManager instances.')
        self.connect(refresh_button, SIGNAL('clicked()'), self._refresh)
        button_layout.addWidget(refresh_button)

        exit_button = QPushButton('Close', self)
        exit_button.setFocusPolicy(Qt.NoFocus)
        exit_button.setToolTip("Makes the window invisible. Use 'display' to make it visible again")
        self.connect(exit_button, SIGNAL('clicked()'), self._hide)
        button_layout.addWidget(exit_button)

        grid_layout.addLayout(button_layout, 1, 0)

        result = QWidget()
        result.setLayout(grid_layout)
        return result

    # callback for the Close button.
    def _hide(self):
        self.setVisible(False)

    # callback for the Refresh button. This button is the way around the
    # design limitation that we have for now: if the user changes a
    # parameter from the command line, the GUI is not able to pick it
    # up transparently, because the 'model' (as in MVC) cannot be
    # updated when an astropy object is changed by direct reference to
    # it. Astropy doesn't provide for notifications to be sent from its
    # guts when, say, parameter values are directly changed. Thus the
    # workaround is to have the user explicitly act on the GUI to force
    # its refresh on screen.
    def _refresh(self):
        for k in range(self.count()):

            # this construct depends on the details of the window build
            # and layout sequence as implemented in module sp_widget.
            window = self.widget(k).layout().itemAt(0).widget().widget(0)

            # it's not enough to send a generic signal to tell the model
            # (as in MVC) that it changed. We have to resort to completely
            # removing all rows from the tree, and then adding them back.
            # This somehow may have to do with the Qt nonblock mechanism,
            # because when in blocking mode, a direct, generic signal
            # works as expected.
            window.model.beginRemoveRows(window.treeView.rootIndex(),
                                         0, window.model.rowCount()-1)
            component_list = []
            row_range = range(window.model.rowCount())
            for k in row_range:
                item = window.model.item(0).getDataItem()
                component_list.append(item)
                window.model.removeRow(0)
            window.model.endRemoveRows()
            for k in row_range:
                component = component_list[k]
                name = models_registry.getComponentName(component)
                window.model.addToModel(name, component)

    # Overrides the default behavior so as to ignore window closing
    # requests (such as from the platform-dependent red X button) and
    # respond instead by just making the window invisible. This in
    # fact renders the widget impossible to close except by terminating
    # the Python interactive session. This is required by the nature of
    # the underlying QApplication. Only one QApplication can exist, and
    # only one can be created in any given Python session. A (desirable)
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

# The first time this function is called, it starts the QApplication
# and runs the GUI, and passes to it the first instance of a model
# manager. Subsequent calls will just  add a new model manager and
# make the widget visible.
def _displayGUI(manager, name):
    global __dialog
    if not __dialog:
        global __app
        __app = QApplication([])
        if __app is None:
            __app = pyqtapplication()
        __dialog = _ModelManagerWidget(manager.manager, name)
    else:
        __dialog._addManager(manager.manager, name)
        __dialog.setVisible(True)


# Main class. The user interactively creates instances of this to
# manage a spectral model in each instance. For now, each instance
# starts with an empty model by default; the user then uses the GUI
# to add spectral functions to the model, and modify their parameter
# values and sequence of evaluation in the composite.

class ModelManager(object):
    """ Instances of this class hold a composite spectral model.

    A ModelManager instance contains a user-definable list of spectral
    components from astropy.modeling.functional_models. From that list,
    a SummedCompositeModel is built and used to compute flux values,
    given spectral coordinate values. The list of spectral components
    in any particular instance of ModelManager is displayed on screen,
    in a tabbed pane, and can be interacted with so that individual
    parameter values can be examined or set by the user.

    This class is basically a wrap-around of SpectralModelManager, to
    make it available to interactive users with a Python command prompt.
    Programmatic use should resort to instances of SpectralModelManager
    directly.

    Changes in the components or the structure of the model manager
    trigger signals of type SignalModelChanged. These signals can be
    caught with code that looks like this:

    managerInstance.changed.connect(handleSignal.....)


    Parameters
    ----------
    name: str, optional
      The name string that goes in the tab associated with the
      ModelManager instance. If no name is provided, a name will
      be picked from the next unused string in the sequence
      '1', '2', '3', ....

    model: list, optional
      List with instances of spectral components from
      astropy.modeling.functional_models. If not provided,
      the instance will be initialized with an empty
      SummedCompositeModel.

    Example:
    -------
      How to create an instance:

        mm1 = ModelManager()
        mm2 = ModelManager('test1')
        mm3 = ModelManager(model=[Gaussian1D(1.,1.,1.)])
        mm4 = ModelManager(model=[Gaussian1D(1.,1.,1.), Lorentz1D(1.,1.,1.)])
        mm5 = ModelManager("test2", [Gaussian1D(1.,1.,1.), Lorentz1D(1.,1.,1.)])

      How to catch a signal:

        >>> import sp_model_manager as mm
        >>> def f():
        ...   print 'Hello!'
        ...
        >>> a = mm.ModelManager()
        >>> a.changed.connect(f)
        >>>                          # do some interaction with the GUI, changing
        >>> Hello!                   # spectral component parameters or the model
        Hello!                       # structure.
        Hello!
        Hello!
        Hello!
        >>>
    """
    def __init__(self, name=None, model=None):

        self.manager = SpectralModelManager(model)

        _displayGUI(self, name)

        # this just propagates up the signals emitted by
        # the SpectralModelManager instance just created.
        self.changed = SignalModelChanged()
        self.manager.changed.connect(self._broadcastModelChange)

    def _broadcastModelChange(self):
        self.changed()

    # Use delegation to decouple the ModelManager API from
    # the GUI model manager API.

    def add(self, component):
        ''' Adds a new spectral component to the manager.

        This might be easier to do using the GUI itself,
        after all, that is the purpose of this class in
        the first place.

        Parameters
        ----------
        component: astropy.modeling.Fittable1DModel
          The component to be added to the manager.

        '''
        self.manager.addComponent(component)

    @property
    def selected(self):
        ''' Gets the currently selected component in the GUI.

        Returns
        -------
        The currently selected component in the GUI, or None

        '''
        return self.manager.selectedComponent()

    @property
    def components(self):
        ''' Gets a list with all components in the manager.

        Returns
        -------
        list with all components in the manager.

        '''
        return self.manager.components

    def setArrays(self, x, y):
        ''' Defines the region in spectral coordinate vs. flux
        'space' to which the components in the model should refer
        to.

        For now, this region is being defined by the data arrays
        associated with the observational data at hand. The region
        could conceivably be defined by any other means, as long
        as the functional components can then use the region data
        to initialize their parameters with sensible values.

        This region is used by code in module sp_adjust. If no
        X and/or Y arrays are provided via this method, spectral
        components added to the SummedCompositeModel will be
        initialized to a default set of parameter values.

        Parameters
        ----------
        x: numpy array
          Array with spectral coordinates
        y: numpy array
          Array with flux values

        '''
        self.manager.setArrays(x, y)

    def spectrum(self, wave):
        ''' Computes the SummedCompositeModel for a given
        array of spectral coordinate values.

        Parameters
        ----------
        wave: numpy array
          Array with spectral coordinate values.

        Returns
        -------
        A numpy array with flux values.

        '''
        return self.manager.spectrum(wave)


if __name__ == "__main__":
    mm = ModelManager()
