import inspect
import numpy as np

from ..external.qt import QtGui, QtCore

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

class CubeDataTreeItem(QtGui.QStandardItem):
    def __init__(self, item, name="Cube Data"):
        super(CubeDataTreeItem, self).__init__()
        self.is_visible = True
        self._item = item
        self._layer_items = []
        self.setText(name)
        self.setData(item)

        self.setFlags(self.flags() | QtCore.Qt.ItemIsEnabled |
                      QtCore.Qt.ItemIsEditable |
                      QtCore.Qt.ItemIsUserCheckable)

        self.setCheckState(QtCore.Qt.Checked)

    @property
    def item(self):
        return self._item

    @property
    def layers(self):
        return self._layer_items

    def add_layer_item(self, layer_data_item):
        if not isinstance(layer_data_item, LayerDataTreeItem):
            raise TypeError("Layer is not of type LayerDataTreeItem.")

        self._layer_items.append(layer_data_item)

    def remove_layer(self, layer):
        if layer in self._layer_items:
            self._layer_items.remove(layer)


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
        self._name = name
        self._item = item
        self._layer_items = []
        self.setText(name)
        self.setData(item)

        self.setFlags(self.flags() | QtCore.Qt.ItemIsEnabled |
                      QtCore.Qt.ItemIsEditable |
                      QtCore.Qt.ItemIsUserCheckable)

        self.setCheckState(QtCore.Qt.Checked)

    @property
    def parent(self):
        return None

    @property
    def item(self):
        return self._item

    @property
    def layers(self):
        return self._layer_items

    @property
    def name(self):
        return self._name

    def add_layer_item(self, layer_data_item):
        if not isinstance(layer_data_item, LayerDataTreeItem):
            raise TypeError("Layer is not of type LayerDataTreeItem.")

        self._layer_items.append(layer_data_item)

    def remove_layer(self, layer):
        if layer in self._layer_items:
            self._layer_items.remove(layer)


class LayerDataTreeItem(QtGui.QStandardItem):
    sig_updated = QtCore.Signal()

    def __init__(self, parent, filter_mask, rois=None, collapse='mean',
                 name="Layer", node_parent=None):
        super(LayerDataTreeItem, self).__init__()
        self.setColumnCount(2)
        self._parent = parent
        self._node_parent = node_parent
        self._rois = rois
        self._collapse = collapse
        self._name = name
        self._model_items = []

        if isinstance(self.parent, CubeDataTreeItem):
            self._filter_mask_cube = filter_mask
            self._filter_mask = None
            self._item, self._filter_mask = self._parent.item.collapse_to_spectrum(
                self._collapse, filter_mask=self._filter_mask_cube)
        else:
            self._filter_mask_cube = None
            self._filter_mask = filter_mask
            self._item = self._parent.item

        self.setFlags(self.flags() | QtCore.Qt.ItemIsEnabled |
                      QtCore.Qt.ItemIsEditable |
                   QtCore.Qt.ItemIsUserCheckable)
        self.setCheckState(QtCore.Qt.Checked)

        self.set_data()

    def set_data(self):
        self.setText(self._name)
        self.setData(self._parent.item[self._filter_mask])

    def update_data(self, item=None, filter_mask=None, collapse=None):
        if item is not None:
            self._item = item

        if filter_mask is not None:
            self._filter_mask_cube = filter_mask

        if collapse is not None:
            self._collapse = collapse

        if isinstance(self.parent, CubeDataTreeItem):
            self._item, self._filter_mask = self._parent.item.collapse_to_spectrum(
                self._collapse, filter_mask=self._filter_mask_cube)

        self.set_data()

    @property
    def model(self):
        """This returns a class object."""
        return np.sum([m.model for m in self._model_items])

    @property
    def item(self):
        return self._item

    @property
    def filter_mask(self):
        return self._filter_mask

    @property
    def parent(self):
        return self._parent

    @property
    def node_parent(self):
        return self._node_parent

    @property
    def name(self):
        return self._name

    def add_model_item(self, model_data_item):
        self._model_items.append(model_data_item)

    def sig_update(self):
        pass
        # self.sig_updated.emit()

    def remove_self(self):
        self.parent.remove_layer(self)

        if self._node_parent is not None:
            self._node_parent.remove_layer(self)

    def remove_model(self, model):
        print("Trying to remove {} for {}".format(model, self))
        if model in self._model_items:
            print("Model is removed")
            self._model_items.remove(model)


class ModelDataTreeItem(QtGui.QStandardItem):


    #TODO this is were to intervene when adding model parameter attributes to the GUI tree


    def __init__(self, parent, model, name="Model"):
        super(ModelDataTreeItem, self).__init__()
        self.setColumnCount(2)
        self._parent = parent
        self._model = model
        self._parameters = []
        self.setText(name)

        self.setFlags(self.flags() & ~QtCore.Qt.ItemIsUserCheckable)

        self._setup_children()

    @property
    def parent(self):
        return self._parent

    @property
    def model(self):
        return self._model

    def _setup_children(self):
        args = inspect.getargspec(self._model.__init__)
        keywords = args[0]
        defaults = self._model.parameters

        for i, key in enumerate(keywords[1:]):
            para_name = ParameterDataTreeItem(self, key, defaults[i])
            para_value = ParameterDataTreeItem(self, key, defaults[i], True)
            self._parameters.append((para_name, para_value))

            self.appendRow([para_name, para_value])

            # We might have to change the representation here. Right now, a
            # parameter is represented by a name and a editable value, both
            # displayed on the same tree row, as created by the line of code above.
            # A new representation would display the parameter name and possibly
            # a non-editable representation of the value, in a tree row. That row
            # would be followed by the set of parameter attributes, set up as
            # children of the parameter name row. The set of parameter attributes
            # would include an editable version of the parameter value itself. That
            # way we can achieve the uniform look-and-feel required in a multi-level
            # tree depiction.
            # We will also need attribute representation subtypes: right now, a double
            # and a boolean (for the 'fixed' attribute) are required. In the future,
            # we may also require a 'function' type, for the 'tied' attribute.
            #
            # The changes above already exist in the master branch. Use that code as
            # a guide on how to implement it here.

    def update_parameter(self, name, value):
        setattr(self._model, name, float(str(value)))
        self._parent.sig_update()

    def refresh_parameters(self):
        print("Model refreshed")
        for i in range(len(self.rowCount())):
            self.removeRow(i)

        self._setup_children()


class ParameterDataTreeItem(QtGui.QStandardItem):
    def __init__(self, parent, name, value, is_editable=False):
        super(ParameterDataTreeItem, self).__init__()
        self.setEditable(is_editable)
        self._parent = parent
        self._name = name
        self._value = value

        self.setFlags(self.flags() & ~QtCore.Qt.ItemIsUserCheckable)

        if not is_editable:
            self.setData(str(name), role=QtCore.Qt.DisplayRole)
        else:
            self.setData(str(value))
            self.setText(str(value))

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
