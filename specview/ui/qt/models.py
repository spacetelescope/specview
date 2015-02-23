from PyQt4 import QtGui, QtCore, Qt
from astropy.units import Unit
from astropy.modeling import models
import numpy as np
from specview.io import read_data
from specview.core import Layer


class SpectrumDataTreeItem(QtGui.QStandardItem):
    """
    Subclasses QStandarditem; provides the base class for all items listed
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
    def __init__(self, parent, mask, rois, name="Layer"):
        super(LayerDataTreeItem, self).__init__()
        self._parent = parent
        self._mask = mask
        self._rois = rois
        self._models = []

        self.setText(name)
        self.setData((self._parent, self._mask, self._rois))

    @property
    def item(self):
        if self._mask is not None:
            self._parent.item.mask = np.logical_not(self._mask)

        return self._parent.item

    def add_model(self, model):
        self._models.append(model)


class ModelDataTreeItem(QtGui.QStandardItem):
    def __init__(self, parent, model):
        super(ModelDataTreeItem, self).__init__()
        self._parent = parent
        self._model = model


class SpectrumDataTreeModel(QtGui.QStandardItemModel):
    """
    Custom TreeView model for displaying DataSetItems.
    """
    def __init__(self):
        super(SpectrumDataTreeModel, self).__init__()
        self._items = []

    def create_data(self, nddata, name=""):
        ds_item = SpectrumDataTreeItem(nddata, name)

        self._items.append(ds_item)
        self.appendRow(ds_item)

    def create_layer(self, parent, mask, rois=None):
        print("Creating layer...")
        if not isinstance(parent, SpectrumDataTreeItem):
            raise TypeError("Expected type SpectrumDataTreeItem, "
                            "got {}".format(str(type(parent))))

        layer_item = LayerDataTreeItem(parent, mask, rois)
        parent.add_layer(layer_item)
        parent.appendRow(layer_item)

    def add_model(self, parent, model):
        print("Adding model")

        model_item = ModelDataTreeItem(parent, model)
        parent.add_model(model_item)

