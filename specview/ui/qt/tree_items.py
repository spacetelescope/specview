import re
import inspect

from ...external.qt import QtGui, QtCore
import numpy as np

from specview.core.data_objects import SpectrumData


# RE pattern to decode scientific and floating point notation.
_pattern = re.compile(r"[+-]?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?")
def float_check(value):
    """ Checks for a valid float in either scientific or floating point notation"""
    substring = _pattern.findall(str(value))
    if substring:
        number = substring[0]
        return float(number)
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


class LayerDataTreeItem(QtGui.QStandardItem):
    # TODO: get rid of nasty try/excepts
    try:
        sig_updated = QtCore.pyqtSignal()
    except AttributeError:
        sig_updated = QtCore.Signal()

    def __init__(self, parent, mask, rois, name="Layer"):
        super(LayerDataTreeItem, self).__init__()
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
        return np.sum(self._models)

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
        pass
        # self.sig_updated.emit()


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
        defaults = self._model.parameters

        for i, key in enumerate(keywords[1:]):
            para_name = ParameterDataTreeItem(self, key, defaults[i])
            para_value = ParameterDataTreeItem(self, key, defaults[i], True)
            self._parameters.append((para_name, para_value))
            self.appendRow([para_name, para_value])

            # parameter attributes.
            attr_fixed = self._model.fixed[key]
            attr_name = ParameterDataTreeItem(self, 'fixed', attr_fixed)
            attr_value = BooleanParameterDataTreeItem(self, 'fixed', attr_fixed)
            para_name.appendRow([attr_name, attr_value])

    def update_parameter(self, name, value):
        value = float_check(value)
        if value:
            setattr(self._model, name, value)
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

        self.setDataValue(name, value, is_editable)

    def setDataValue(self, name, value, is_editable):
        if not is_editable:
            self.setData(str(name), role=QtCore.Qt.DisplayRole)
        else:
            self.setData(str(value))
            self.setText(str(value))

    @property
    def parent(self):
        return self._parent


class BooleanParameterDataTreeItem(ParameterDataTreeItem):
    ''' Handles boolean attribute value via a checkbox '''
    def __init__(self, parent, name, value):
        super(BooleanParameterDataTreeItem, self).__init__(parent, name, value, is_editable=True)
        self.setCheckable(True)

    def setDataValue(self, name, value, is_editable):
        self.setData(value, role=QtCore.Qt.CheckStateRole)

