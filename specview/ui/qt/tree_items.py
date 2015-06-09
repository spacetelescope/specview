import inspect
import re
import math

from ...external.qt import QtGui, QtCore
import numpy as np

from specview.core.data_objects import SpectrumData

# RE pattern to decode scientific and floating point notation.
_pattern = re.compile(r"[+-]?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?")

def float_check(value):
    """ Checks for a valid float in either scientific or floating point notation"""
    substring = _pattern.findall(str(value))
    if substring:
        number = float(substring[0])
        if len(substring) > 1:
            number *= math.pow(10., int(substring[1]))
        return number
    else:
        return False


class SpectrumDataTreeItem(QtGui.QStandardItem):
    """Subclasses QStandarditem; provides the base class for all items listed
    in the data set tree view. This currently acts as a wrapper around the
    SpectrumData object. This class will probably be discarded in the future in
    favor of a full subclass of AbstractModel.

    Note
    ----
    This currently treats `Models` as Qt-level discrete objects. This will
    change in the future.
    """
    def __init__(self, item, name="Data"):
        super(SpectrumDataTreeItem, self).__init__()
        self.setEditable(True)

        self._item = item
        self._layers = []
        self.setText(name)
        self.setData(item)

    @property
    def parent(self):
        return None

    @property
    def item(self):
        return self._item

    @property
    def layers(self):
        return self._layers

    def add_layer(self, layer):
        if not isinstance(layer, LayerDataTreeItem):
            raise TypeError("Layer is not of type LayerViewItem.")

        self._layers.append(layer)

    def remove_layer(self, layer):
        self._layers.remove(layer)


class SignalUpdated(QtCore.QObject):
    # You can only have pyqtSignal() or Signal() in classes that are derived from QObject.
    # (http://comments.gmane.org/gmane.comp.python.pyqt-pykde/28223)

    # TODO: get rid of nasty try/excepts
    try:
        sig_updated = QtCore.pyqtSignal()
    except AttributeError:
        sig_updated = QtCore.Signal()

    def emit(self):
        self.sig_updated.emit()


class LayerDataTreeItem(QtGui.QStandardItem):
    def __init__(self, parent, mask, rois, name="Layer"):
        super(LayerDataTreeItem, self).__init__()

        self.signal_updated = SignalUpdated()

        self.setColumnCount(2)
        self._parent = parent
        self._mask = mask
        self._rois = rois
        self._models = []

        x = parent.item.x
        y = parent.item.y
        self._data = SpectrumData(x[~mask], y[~mask])

        self.setText(name)
        self.setData(self._data)

    @property
    def model(self):
        """This returns a class object."""

        #TODO here is the place to add support for a compound model expression handler.

        compound_model = np.sum(self._models)
        return compound_model

    @property
    def item(self):
        return self._data

    @property
    def parent(self):
        return self._parent

    def add_model(self, model):
        self._models.append(model)

    # --- signals
    def sig_update(self):
        self.signal_updated.emit()


class ModelDataTreeItem(QtGui.QStandardItem):
    def __init__(self, parent, model, name="Model"):
        super(ModelDataTreeItem, self).__init__()
        self.setColumnCount(2)
        self._parent = parent
        self._model = model
        self._parameters = []
        self.setText(name)

        self._setup_children()

    @property
    def parent(self):
        return self._parent

    def _setup_children(self):
        args = inspect.getargspec(self._model.__init__)
        keywords = args[0]
        values = self._model.parameters

        for i, key in enumerate(keywords[1:]):
            para_name = ParameterDataTreeItem(self, key, values[i])
            para_value = ParameterValueDataTreeItem(self, key, values[i])
            self._parameters.append((para_name, para_value))
            self.appendRow([para_name, para_value])

            # Parameter attributes are attached to the parameter name/value tree node.
            # One could argue that in fact we need a sort of parent node to hold the
            # parameter, and sub-nodes to hold its attributes AND value. But since
            # that parent node would be rendered with the name and value anyway, the
            # end result is the same, as far as the GUI goes. It remains to be seen
            # if this will affect the three structure in any undesirable way.

            parameter = getattr(self._model, key)
            attr_fixed = self._model.fixed[key]

            attr_name = ParameterDataTreeItem(para_name, 'fixed', attr_fixed)
            attr_value = BooleanAttributeValueDataTreeItem(para_name, 'fixed', attr_fixed)
            para_name.appendRow([attr_name, attr_value])

            attr_name = ParameterDataTreeItem(para_name, 'min', parameter.min)
            attr_value = AttributeValueDataTreeItem(para_name, 'min', parameter.min)
            para_name.appendRow([attr_name, attr_value])

            attr_name = ParameterDataTreeItem(para_name, 'max', parameter.max)
            attr_value = AttributeValueDataTreeItem(para_name, 'max', parameter.max)
            para_name.appendRow([attr_name, attr_value])

    def update_value(self, name, value):
        setattr(self._model, name, value)
        self._parent.sig_update()

    def refresh_parameters(self):
        print("Model refreshed")
        for i in range(len(self.rowCount())):
            self.removeRow(i)
        self._setup_children()


class ParameterDataTreeItem(QtGui.QStandardItem):
    ''' Class that holds parameter and attribute names on the tree.

        A name is a non-editable string. It is used to build the
        name field in a tree row that displays either a parameter
        name/value pair, or a parameter attribute name/value pair.
     '''
    def __init__(self, parent, name, value):
        super(ParameterDataTreeItem, self).__init__()
        self.setEditable(False)
        self._parent = parent
        self._name = name
        self._value = value

        self.setDataValue(name, value)

    def setDataValue(self, name, value):
        self.setData(str(name), role=QtCore.Qt.DisplayRole)

    @property
    def parent(self):
        return self._parent


class ParameterValueDataTreeItem(ParameterDataTreeItem):
    ''' Subclasses the base class to add the ability to edit
        the field and have it's value propagated to the
        underlying astropy object.

        This class is used to build the 'value' field in a tree
        row that displays either a parameter name/value pair, or
        a parameter attribute name/value pair.
    '''
    def __init__(self, parent, name, value):
        super(ParameterValueDataTreeItem, self).__init__(parent, name, value)
        self.setEditable(True)

    def setDataValue(self, name, value):
        self.setData(value)
        self.setText(str(value))

    def update_value(self, name, value):
        value = float_check(value)
        if value:
            self._parent.update_value(name, value)


class AttributeValueDataTreeItem(ParameterValueDataTreeItem):
    ''' Subclasses the parameter value class to handle parameter
        attribute values instead of parameter values.
    '''
    # An attribute is a child of a parameter. A parameter in turn
    # is a child of a model.
    def update_value(self, name, value):
        self._value = value
        parameter = getattr(self._parent._parent._model, self._parent._name)
        setattr(parameter, name, value)
        # the layer that has to be signaled is 3 levels above the attribute.
        self._parent._parent._parent.sig_update()

    def setDataValue(self, name, value):
        self.setData(value)
        self.setText(str(value))


class BooleanAttributeValueDataTreeItem(ParameterValueDataTreeItem):
    ''' Subclasses the parameter value class to handle parameter
        boolean attribute values. These are represented by checkboxes.
    '''
    # An attribute is a child of a parameter. A parameter in turn
    # is a child of a model.
    def __init__(self, parent, name, value):
        super(BooleanAttributeValueDataTreeItem, self).__init__(parent, name, value)
        self.setCheckable(True)

    def setDataValue(self, name, value):
        # this method is necessary here to ensure that the proper role is
        # assigned to the tree node. Otherwise we may see a 'True' or 'False'
        # string displayed beside the checkbox (the default way Qt displays
        # checkable nodes with other role types).
        self.setData(value, role=QtCore.Qt.CheckStateRole)

    def update_value(self, name, value):
        # Both the passed name and value are ignored. We use the internally
        # stored name, and the value is irrelevant because the result of
        # updating a boolean is simply toggling it.
        parameter = getattr(self._parent._parent._model, self._parent._name)
        if self.checkState() == QtCore.Qt.Checked:
            setattr(parameter, self._name, True)
        else:
            setattr(parameter, self._name, False)
        # the layer that has to be signaled is 3 levels above the attribute.
        # But, avoid signaling for now. Otherwise, a new model and its layer
        # get created every time an attribute gets changed by the user.
        # self._parent._parent._parent.sig_update()
