import inspect
import numpy as np

from ..external.qt import QtGui, QtCore


class CubeDataTreeItem(QtGui.QStandardItem):
    def __init__(self, item, name="Cube Data"):
        super(CubeDataTreeItem, self).__init__()
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
    def __init__(self, item, name="Spectrum Data"):
        super(SpectrumDataTreeItem, self).__init__()
        self.setEditable(True)

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
                 name="Layer"):
        super(LayerDataTreeItem, self).__init__()
        self.setColumnCount(2)
        self._parent = parent
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

    def add_model_item(self, model_data_item):
        self._model_items.append(model_data_item)

    def sig_update(self):
        pass
        # self.sig_updated.emit()

    def remove_model(self, model):
        print("Trying to remove {} for {}".format(model, self))
        if model in self._model_items:
            print("Model is removed")
            self._model_items.remove(model)


class ModelDataTreeItem(QtGui.QStandardItem):
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
