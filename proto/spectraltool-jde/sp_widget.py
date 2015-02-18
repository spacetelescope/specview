from __future__ import division

import re
import numpy as np
from astropy.modeling import Parameter, Fittable1DModel, SummedCompositeModel
from astropy.modeling.polynomial import PolynomialModel

import signal_slot
import models_registry
import sp_adjust

from PyQt4.QtCore import *
from PyQt4.QtGui import *

FONT_SIZE_INCREASE = 2


# Finds the level at which a tree is being selected.
# Also finds the index for the zero-th level parent
# that is associated with the selected item.

def findLevelAndIndex(indices):
    if len(indices) <= 0:
        return -1, -1
    level = 0
    index0 = -1
    if len(indices) > 0:
        index0 = indices[0]
        while index0.parent().isValid():
            index0 = index0.parent()
            level += 1
    return level, index0


# Subclasses QTreeView in order to detect selections on tree elements
# and enable/disable other GUI elements accordingly.

class _MyQTreeView(QTreeView):
    def __init__(self, model):
        super(_MyQTreeView, self).__init__()
        # Model is required so we can have access to all
        # rows, not just the currently selected one.
        self.model = model

        # Default behavior is the same as the superclass'.
        self.b_up = None
        self.b_down = None
        self.b_delete = None

    # By providing button instances, the specialized
    # behavior is triggered on.
    def setButtons(self, b_up, b_down, b_delete):
        self.b_up = b_up
        self.b_down = b_down
        self.b_delete = b_delete
        self.b_up.setEnabled(False)
        self.b_down.setEnabled(False)
        self.b_delete.setEnabled(False)

    # Overrides QTreeView to provide
    # sensitivity to selection events.
    def selectionChanged(self, selected, deselected):
        # IndexError may happen in normal GUI usage and it's normal.
        try:
            self._handleTreeSelectionEvent(selected, deselected)
        except IndexError:
            pass

    # Overrides QTreeView to capture and handle a data changed event.
    # These data changes occur in the model associated with the tree,
    # when a Data object gets changed, such as when the user types in
    # a new value for a Parameter instance.
    def dataChanged(self, top, bottom):
        self.emit(SIGNAL("dataChanged"), 0)
        super(_MyQTreeView, self).dataChanged(top, bottom)

    # Here is the logic to gray out buttons based on context.
    def _handleTreeSelectionEvent(self, selected, deselected):

        # only acts if actual button instances exist.
        if self.b_up and self.b_down and self.b_delete:

            # nothing is selected, so no button action is allowed.
            if selected.count() == 0 or selected.count() > 1:
                self.b_up.setEnabled(False)
                self.b_down.setEnabled(False)
                self.b_delete.setEnabled(False)

            # one row is selected, but behavior depends
            # on how many rows there are in the tree.
            else:
                # if a row is selected, it can always be deleted.
                self.b_delete.setEnabled(True)

                if self.model.rowCount() == 1:
                    # only one row in tree, thus only deletion is allowed.
                    self.b_up.setEnabled(False)
                    self.b_down.setEnabled(False)
                else:
                    # two or more rows in tree; see which one is selected.
                    # Watch out for the level though, must be root level.
                    level, index0 = findLevelAndIndex(selected.indexes())
                    row = index0.row()
                    if row > 0 and row < (self.model.rowCount() - 1):
                        # selected row is in the middle; can be moved up or down.
                        self.b_up.setEnabled(True)
                        self.b_down.setEnabled(True)
                    elif row == 0:
                        # selected row is top row; can only be moved down.
                        self.b_up.setEnabled(False)
                        self.b_down.setEnabled(True)
                    else:
                        # selected row is bottom row; can only be moved up.
                        self.b_up.setEnabled(True)
                        self.b_down.setEnabled(False)


# Base window that holds a tree widget that supports contextual menus.
# It needs an instance of QStandardItemModel in order to build the tree.

class _BaseWindow(QWidget):
    def __init__(self, model):
        QWidget.__init__(self)

        self.model = model

        font = QFont(self.font())
        font.setPointSize(font.pointSize() + FONT_SIZE_INCREASE)
        self.setFont(font)
        QToolTip.setFont(font)

        self.treeView = _MyQTreeView(self.model)
        self.treeView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.treeView.customContextMenuRequested.connect(self.openMenu)
        self.treeView.setModel(self.model)

        grid_layout = QGridLayout()
        grid_layout.addWidget(self.treeView, 0, 0)

        # button_layout is not used by this class but provides a
        # place where sub classes can put in their own widgets.
        self.button_layout = QHBoxLayout()
        self.button_layout.addStretch()
        grid_layout.addLayout(self.button_layout, 1, 0)

        self.setLayout(grid_layout)

    def openMenu(self, position):
        raise NotImplementedError

    # Returns the selected model.
    def getSelectedModel(self):
        indexes = self.treeView.selectedIndexes()
        if len(indexes) > 0:
            level, index = self.findTreeLevel()
            if len(indexes) > 0:
                data = self.model.item(index.row()).item
                return data
        return None

    # Returns the level at which the tree is being selected.
    # Also returns the index for the zero-th level parent that
    # is associated with the selected item.
    def findTreeLevel(self):
        indices = self.treeView.selectedIndexes()
        return findLevelAndIndex(indices)

    # Connects a slot to the "triggered" signal in a QWidget.
    # This is used to associate callbacks to contextual menus.
    def createAction(self, widget, text, slot=None, shortcut=None,
                     icon=None, tip=None, checkable=False):
        action = QAction(text, widget)
        action.setCheckable(checkable)
        if icon is not None:
            action.setIcon(QIcon("/%s.png" % icon))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            action.triggered.connect(slot)
        return action


# Window with the active spectral components -------------------------------------------

class _SpectralModelsGUI(object):
    def __init__(self, components):
        self.model = ActiveComponentsModel(name="Active components")
        self.model.addItems(components)

        self.window = _SpectralModelsWindow(self.model)

        self.mapper = QDataWidgetMapper()
        self.mapper.setModel(self.model)
        self.mapper.addMapping(self.window.treeView, 0)

        # TODO use QDataWidgetMapper
        # this violation of MVC design principles is necessary
        # so our model manager class can work with the modified
        # code in modelmvc.py. This probably could be done via
        # the QDataWidgetMapper stuff instead.
        self.model.setWindow(self.window)

    @property
    def model(self):
        return self._model

    @model.setter
    def model(self, model):
        self._model = model

    def updateModel(self, component):
        self._model.addOneElement(component)
        self.window.emit(SIGNAL("treeChanged"), 0)

    def getSelectedModel(self):
        return self.window.getSelectedModel()


class _SpectralModelsWindow(_BaseWindow):
    def __init__(self, model):
        super(_SpectralModelsWindow, self).__init__(model)

        # Contextual menus do not always work under ipython
        # non-block mode. These buttons are an alternative
        # way of implementing the same actions.

        up_button = QPushButton('Up', self)
        up_button.setFocusPolicy(Qt.NoFocus)
        up_button.setToolTip('Moves selected component up')
        self.connect(up_button, SIGNAL('clicked()'), self.moveComponentUp)
        self.button_layout.addWidget(up_button)

        down_button = QPushButton('Down', self)
        down_button.setFocusPolicy(Qt.NoFocus)
        down_button.setToolTip('Moves selected component down')
        self.connect(down_button, SIGNAL('clicked()'), self.moveComponentDown)
        self.button_layout.addWidget(down_button)

        delete_button = QPushButton('Delete', self)
        delete_button.setFocusPolicy(Qt.NoFocus)
        delete_button.setToolTip("Delete selected component from ModelManager instance")
        self.connect(delete_button, SIGNAL('clicked()'), self.deleteComponent)
        self.button_layout.addWidget(delete_button)

        # setup to gray out buttons based on context.
        self.treeView.setButtons(up_button, down_button, delete_button)

    # contextual menu
    def openMenu(self, position):
        self.position = position
        level, index = self.findTreeLevel()
        if index.isValid():
            menu = QMenu()
            menu.addAction(self.createAction(menu, "Delete component", self.deleteComponent))
            row = index.row()
            if row > 0:
                menu.addAction(self.createAction(menu, "Move component up", self.moveComponentUp))
            if row < self.model.rowCount() - 1:
                menu.addAction(self.createAction(menu, "Move component down", self.moveComponentDown))

            # We would use code like this in case we need contextual
            # menus at other levels in the tree besides the first level.
            #
            #            level = self.findTreeLevel()
            #            if level == 0:
            #                menu.addAction(self.createAction(menu, "Delete component", self.deleteComponent))
            #                row = self.treeView.indexAt(self.position).row()
            #                if row > 0:
            #                    menu.addAction(self.createAction(menu, "Move component up", self.moveComponentUp))
            #                if row < self.model.rowCount()-1:
            #                    menu.addAction(self.createAction(menu, "Move component down", self.moveComponentDown))
            #            elif level == 1:
            #                 placeholder for edit parameter functionality.
            #            elif level == 2:
            #                menu.addAction(self.createAction(menu, "Edit parameter value", self.editParameterValue))

            menu.exec_(self.treeView.viewport().mapToGlobal(position))

    # Callbacks for contextual menus and buttons. The 'treeChanged'
    # signal is emitted so caller code can be notified when buttons
    # and menus are activated and the trees get re-arranged.
    def deleteComponent(self):
        level, index = self.findTreeLevel()
        if level >= 0:
            self.model.takeRow(index.row())
            self.treeView.clearSelection()
            self.emit(SIGNAL("treeChanged"), index.row())

    def moveComponentUp(self):
        level, index = self.findTreeLevel()
        if level >= 0 and index.row() > 0:
            is_expanded = self.treeView.isExpanded(index)
            items = self.model.takeRow(index.row())
            self.model.insertRow(index.row() - 1, items)
            index_above = self.treeView.indexAbove(index)
            self.treeView.setExpanded(index_above, is_expanded)
            self.treeView.clearSelection()
            self.emit(SIGNAL("treeChanged"), index.row())

    def moveComponentDown(self):
        level, index = self.findTreeLevel()
        if level >= 0 and index.row() < self.model.rowCount() - 1:
            is_expanded = self.treeView.isExpanded(index)
            items = self.model.takeRow(index.row())
            self.model.insertRow(index.row() + 1, items)
            index_below = self.treeView.indexBelow(index)
            self.treeView.setExpanded(index_below, is_expanded)
            self.treeView.clearSelection()
            self.emit(SIGNAL("treeChanged"), index.row())

# Parameter values can be edited directly from their QStandardItem
# representation. The code below (still incomplete) is an attempt
# to use contextual menus for the same purpose.
#
#    def editParameterValue(self):
#        parameter_index = self.treeView.indexAt(self.position).parent()
#        parameter_row = parameter_index.row()
#
#        function_row = parameter_index.parent().row()
#        item = self.model.item(function_row)
#        function = item.getDataItem()
#
#        for param_name in function.param_names:
#            if function._param_orders[param_name] == parameter_row:
#                break
#        parameter =  function.__getattribute__(param_name)
#
#        print "AstropyModelingTest - line 163: ",  parameter.value



# Window with the spectral component library ------------------------------------------------

class _SpectralLibraryGUI(object):

# Attempt to get classes directly from the models module.
# Doesn't work, need to get classes from Model registry instead.
    # def __init__(self, models_gui):
    #     data = []
    #     for key in models.__all__:
    #         function_metaclass = models.__dict__[key]
    #         if issubclass(function_metaclass, Fittable1DModel):
    #             data.append(function_metaclass)
    #
    #     self.window = LibraryWindow(data, models_gui)

    def __init__(self, models_gui, x, y):
        data = []
        keys = sorted(models_registry.registry.keys())
        for key in keys:
            function = models_registry.registry[key]
            # redundant test for now, but needed in case we
            # switch to introspection from the models registry.
            # if issubclass(function.__class__, Fittable1DModel) or \
            #    issubclass(function.__class__, PolynomialModel):
            # TODO Polynomials do not carry internal instances of
            # Parameter. This makes the code in this module unusable.
            # We need to add special handling tools that can get and
            # set polynomial coefficients. Thus suggests that they
            # were not designed t be mixed in with instances of
            # Fittable1DModel.
            if issubclass(function.__class__, Fittable1DModel):
                data.append(function)

        self.model = SpectralComponentsModel(name="Available components")
        self.model.addItems(data)

        self.window = _LibraryWindow(self.model, models_gui, x, y)

    def getSelectedModel(self):
        return self.window.getSelectedModel()

    def setArrays(self, x, y):
        self.window.setArrays(x, y)

class _LibraryWindow(_BaseWindow):
    def __init__(self, model, models_gui, x, y):
        super(_LibraryWindow, self).__init__(model)
        self.models_gui = models_gui

        # numpy arrays used to instantiate functions.
        self.x = x
        self.y = y

        # Contextual menus do not always work under ipython
        # non-block mode. The Add button is an alternative
        # way of implementing the same action.
        add_button = QPushButton('Add', self)
        add_button.setFocusPolicy(Qt.NoFocus)
        add_button.setToolTip('Adds selected component to active model')
        self.connect(add_button, SIGNAL('clicked()'), self.addComponent)
        self.button_layout.addWidget(add_button)

    # callback for the Add button
    def addComponent(self):
        function = self.getSelectedModel()

        sp_adjust.adjust(function, self.x, self.y)

        self._addComponentToActive(function)
        self.treeView.clearSelection()

    # contextual menu.
    def openMenu(self, position):
        index = self.treeView.indexAt(position)
        if index.isValid():
            menu = QMenu()
            menu.addAction(self.tr("Add component"))
            menu.exec_(self.treeView.viewport().mapToGlobal(position))
            # no need to add an action to this menu since it has only one
            # element. Just do the action straight away.
            item = self.model.item(index.row())
            if item:
                function = item.getDataItem()
                self._addComponentToActive(function)

        self.treeView.clearSelection()

        # This is an attempt to instantiate from the class registry.
        #
        # param_names = inspect.getargspec(meta.__init__)[0]
        # param_values = np.ones(len(param_names)-1)
        #
        # inst = models_registry[name](param_values)
        #
        # cls = type.__new__(type(meta), name, (Fittable1DModel,), {'param_names': param_names[1:]})
        # cls = type(name, (Fittable1DModel,), {'param_names': param_names[1:]})
        #
        # args = {}
        # i = 0
        # for pn in param_names[1:]:
        #     args[pn] = param_values[i]
        #     i += 1
        #
        # inst = cls.__init__(**args)

    def setArrays(self, x, y):
        self.x = x
        self.y = y

    # this method adds the selected component to the active model.
    def _addComponentToActive(self, component):
        name = models_registry.getComponentName(component)

        # this should be done by instantiating from a class, but that is
        # not possible yet (the astropy dev version can't be compiled due
        # to a Cython syntax error...). So we resort to brute force and
        # copy the instances instead.
        component = models_registry.registry[name].copy()
        if component:
            sp_adjust.adjust(component, self.x, self.y)
            self.models_gui.updateModel(component)


# The MVC Model classes -----------------------------------------

# Item classes

# Base item is a QStandardItem with the ability to directly
# hold a reference to the spectral object being represented
# in the tree.
class SpectralComponentItem(QStandardItem):
    def __init__(self, name):
        QStandardItem.__init__(self)
        if name is None:
            name = "None"
        self.setData(name, role=Qt.DisplayRole)
        self.setEditable(False)

    def setDataItem(self, item):
        self.item = item

    def getDataItem(self):
        return self.item

# Value item specializes the base item to make it editable.
# or checkable. The slot connected to the tree model's
# itemChanged signal must be able to differentiate among the
# several possible items, using the 'type' attribute and the
# 'isCheckable' property.
class SpectralComponentValueItem(SpectralComponentItem):
    def __init__(self, parameter, type, checkable=False, editable=True):
        self.parameter = parameter
        self.type = type
        # boolean attributes display attribute
        # value via a checkbox, not text.
        id_str = type
        if not checkable:
            id_str = type + ": " + str(getattr(self.parameter, type))
        SpectralComponentItem.__init__(self, id_str)
        self.setEditable(editable)
        self.setCheckable(checkable)
        # checkbox setup.
        if checkable and getattr(self.parameter, type):
            self.setCheckState(Qt.Checked)


# Model classes

# This class provides the base model for both the active
# and the library windows. The base model handles the
# first tree level, where the component names are held.
class SpectralComponentsModel(QStandardItemModel):
    def __init__(self, name):
        QStandardItemModel.__init__(self)
        self.setHorizontalHeaderLabels([name])

    def addItems(self, elements):
        for element in elements:
            self.addOneElement(element)

    def addOneElement(self, element):
        name = models_registry.getComponentName(element)
        self.addToModel(name, element)

    def addToModel(self, name, element):
        item = SpectralComponentItem(name)
        item.setDataItem(element)
        parent = self.invisibleRootItem()
        parent.appendRow(item)

# This class adds to the base model class the ability to handle
# two additional tree levels. These levels hold respectively
# the parameter names of each component, and each parameter's
# editable attributes.
class ActiveComponentsModel(SpectralComponentsModel):
    def __init__(self, name):
        SpectralComponentsModel.__init__(self, name)
        self.itemChanged.connect(self._onItemChanged)

        # RE pattern to decode scientific notation and
        # floating point notation.
        self._pattern = re.compile(r"[+-]?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?")

    # TODO use QDataWidgetMapper
    # this violation of MVC design principles is necessary
    # so our model manager class can work with the modified
    # code in modelmvc.py. This probably could be done via
    # the QDataWidgetMapper stuff instead.
    def setWindow(self, window):
        self._window = window

    def addToModel(self, name, element):
        # add component to tree root
        item = SpectralComponentItem(name)
        item.setDataItem(element)
        parent = self.invisibleRootItem()
        parent.appendRow(item)
        # now add parameters to component in tree.
        for e in element.param_names:
            par = element.__getattribute__(e)
            if isinstance(par, Parameter):

                # add parameter. Parameter name is followed
                # by its value when displaying in tree.
                parItem = SpectralComponentItem(par.name + ": " + str(par.value))
                parItem.setDataItem(par)
                item.appendRow(parItem)

                # add parameter value and other attributes to parameter element.
                valueItem = SpectralComponentValueItem(par, "value")
                valueItem.setDataItem(par.value)
                parItem.appendRow(valueItem)
                minItem = SpectralComponentValueItem(par, "min")
                minItem.setDataItem(par.min)
                parItem.appendRow(minItem)
                maxItem = SpectralComponentValueItem(par, "max")
                maxItem.setDataItem(par.max)
                parItem.appendRow(maxItem)
                fixedItem = SpectralComponentValueItem(par, "fixed", checkable=True)
                fixedItem.setDataItem(par.fixed)
                parItem.appendRow(fixedItem)
                # 'tied' is not really a boolean, but a callable.
                # How to handle this in a GUI?
                tiedItem = SpectralComponentValueItem(par, "tied", editable=False)
                tiedItem.setDataItem(par.tied)
                parItem.appendRow(tiedItem)

    @property
    def items(self):
        result = []
        for i in range(self.rowCount()):
            result.append(self.item(i).item)
        return result

    def _floatItemChanged(self, item):
        type = item.type
        substring = self._pattern.findall(item.text())
        if substring:
            if hasattr(item, 'parameter'):
                number = substring[0]
                setattr(item.parameter, type, float(number))
                item.setData(type + ": " + number, role=Qt.DisplayRole)
                # parameter name is followed by its value when displaying in tree.
                if type == 'value':
                    item.parent().setData(item.parameter.name + ": " + number, role=Qt.DisplayRole)
        else:
            item.setData(type + ": " + str(getattr(item.parameter, type)), role=Qt.DisplayRole)

    def _booleanItemChecked(self, item):
        type = item.type
        if item.checkState() == Qt.Checked:
            setattr(item.parameter, type, True)
        else:
            setattr(item.parameter, type, False)

    def _onItemChanged(self, item):
        if item.isCheckable():
            self._booleanItemChecked(item)
        else:
            self._floatItemChanged(item)


class SpectralModelManager(QObject):
    """ Basic class to be called by external code.

    It is responsible for building the GUI trees and putting them together
    into a split pane layout. It also provides accessors to the active
    model individual spectral components and to the library functions,
    as well as to the composite spectrum that results from a
    SummedCompositeModel call.

    It inherits from QObject for the sole purpose of being able to
    respond to Qt signals.

    Parameters
    ----------
    model: list, optional
      List with instances of spectral components from
      astropy.modeling.functional_models. If not provided,
      the instance will be initialized with an empty list.

    """
    def __init__(self, model=None):
        super(SpectralModelManager, self).__init__()

        self._model = model
        self.x = None
        self.y = None
        if not self._model:
            self._model = []

        self.changed = SignalModelChanged()
        self.selected = SignalComponentSelected()

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
        self.x = x
        self.y = y

        if  hasattr(self, '_library_gui'):
            self._library_gui.setArrays(self.x, self.y)

    def buildMainPanel(self, model=None):
        """ Builds the main panel with the active and the library
        trees of spectral components.

        Parameters
        ----------
        model: list, optional
          List with instances of spectral components from
          astropy.modeling.functional_models. If not provided,
          the list of components will exist but will be empty.

        Returns
        -------
          instance of QSplitter

        """
        # override whatever model was passed to the constructor.
        # This specific form of the conditional avoids a mishap
        # when self._model is an empty list.
        if model != None:
            self._model = model

        # When called the first time, build the two trees.
        # Subsequent calls must re-use the existing trees
        # so as to preserve user selections and such.
        if not hasattr(self, 'models_gui'):
            self.models_gui = _SpectralModelsGUI(self._model)
            self._library_gui = _SpectralLibraryGUI(self.models_gui, self.x, self.y)

        splitter = QSplitter();
        splitter.addWidget(self.models_gui.window)
        splitter.addWidget(self._library_gui.window)
        splitter.setStretchFactor(0, 0)

        # Tree and data change and click events must
        # be propagated to the outside world.
        self.connect(self.models_gui.window, SIGNAL("treeChanged"), self._broadcastChangedSignal)
        self.connect(self.models_gui.window.treeView, SIGNAL("dataChanged"), self._broadcastChangedSignal)
        self.models_gui.window.treeView.clicked.connect(self._broadcastSelectedSignal)

        return splitter

    def _broadcastChangedSignal(self):
        self.changed()

    def _broadcastSelectedSignal(self):
        self.selected()

    @property
    def treeWidget(self):
        """ Accessor to the tree with rendering of active spectral components.

        Returns
        -------
          instance of QTreeView

        """
        return self.models_gui.window.treeView

    @property
    def components(self):
        """ Accessor to the list with active spectral components.

        Returns
        -------
          instance of list

        """
        return self.models_gui.model.items

    def spectrum(self, wave):
        ''' Computes the SummedCompositeModel for a given
        array of spectral coordinate values.

        Parameters
        ----------
        wave: numpy array
          Array with spectral coordinate values.

        Returns
        -------
        A numpy array with flux values. If no components exist in
        the model, a zero-valued array is returned instead.

        '''
        if len(self.components) > 0:
            sum_of_models = SummedCompositeModel(self.components)
            return sum_of_models(wave)
        else:
            return np.zeros(len(wave))

    def addComponent(self, component):
        ''' Adds a new spectral component to the manager.

        Parameters
        ----------
        component: astropy.modeling.Fittable1DModel
          The component to be added to the manager.

        '''
        component = sp_adjust.adjust(component, self.x, self.y)
        self.models_gui.updateModel(component)

    def getSelectedFromLibrary(self):
        ''' Returns component instance prototype selected in the
        library window. Without

        Returns
        -------
          model selected in the library window.

        '''
        return self._library_gui.getSelectedModel()

    def selectedComponent(self):
        ''' Returns component selected in the active components window.

        Returns
        -------
          component selected in the active components window.

        '''
        return self.models_gui.getSelectedModel()

    def modifyModel(self, new_components):
        ''' Replaces spectral components with new instances.

        This method must be called with a list of components that
        matches the existing components in the model manager active
        list. The method's purpose is to replace the parameter
        values of each component with the values of the paired
        component in the input list. Thus the lists have to match
        perfectly.

        Parameters
        ----------
        new_components: list
          list with instances of astropy.modeling.Fittable1DModel
          to be added to the manager.

        '''
        for i, c in enumerate(self.components):
            nc = new_components[i]
            c.parameters = nc.parameters

            # modify the tree model so the fit results
            # show immediately on the display.
            for j, value in enumerate(c.parameters):
                item = self.models_gui.model.item(i).child(j).child(0)
                item.setData("value: " + str(value), role=Qt.DisplayRole)


class SignalModelChanged(signal_slot.Signal):
    ''' Signals that a change in the model took place. '''

class SignalComponentSelected(signal_slot.Signal):
    ''' Signals that a component has been selected. '''

