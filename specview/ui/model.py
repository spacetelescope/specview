import math
import re
from os import path, sys

import numpy as np

from ..external.qt import QtGui, QtCore

from specview.analysis import model_fitting
from specview.ui.qt.tree_items import (SpectrumDataTreeItem, ModelDataTreeItem,
                                       LayerDataTreeItem, ParameterDataTreeItem,
                                       BooleanAttributeDataTreeItem, float_check)

PATH = path.join(path.dirname(sys.modules[__name__].__file__), "qt", "img")


class SpectrumDataTreeModel(QtGui.QStandardItemModel):
    """Custom TreeView model for displaying DataSetItems."""
    # TODO: get rid of nasty try/excepts
    try:
        sig_added_item = QtCore.pyqtSignal(QtCore.QModelIndex)
        sig_added_fit_model = QtCore.pyqtSignal(ModelDataTreeItem)
        sig_removed_item = QtCore.pyqtSignal(object)
    except AttributeError:
        sig_added_item = QtCore.Signal(QtCore.QModelIndex)
        sig_added_fit_model = QtCore.Signal(ModelDataTreeItem)
        sig_removed_item = QtCore.Signal(object)

    def __init__(self):
        super(SpectrumDataTreeModel, self).__init__()
        self._items = []
        self.itemChanged.connect(self._item_changed)
        self.dc = self.DataCollection(self)
        self.fc = self.FitCollection(self)

    @property
    def items(self):
        return self._items

    @property
    def data_items(self):
        return [x.item for x in self._items]

    # --- protected functions
    def _item_changed(self, item):
        # this is used to propagate changes in the Qt view/model objects
        # to the corresponding astropy objects such as function parameter
        # values and attributes, when their corresponding views on the tree
        # are edited by the user.
        item.update_value(item._name, item.data())

    # --- public functions
    def remove_data_item(self, index, parent_index):
        item = index.model().itemFromIndex(index)
        self.removeRow(index.row(), parent_index)

        if item in self._items:
            self._items.remove(item)

        # if it's a layer
        for sdt_item in self._items:
            if item in sdt_item.layers:
                sdt_item.layers.remove(item)

        self.sig_removed_item.emit(item)

    def create_data_item(self, nddata, name="New"):
        spec_data_item = SpectrumDataTreeItem(nddata, name)
        spec_data_item.setIcon(QtGui.QIcon(path.join(PATH, 'data_set.png')))

        self._items.append(spec_data_item)
        self.appendRow(spec_data_item)
        self.sig_added_item.emit(spec_data_item.index())

        return spec_data_item

    def create_layer(self, parent, mask=None, rois=None):
        if not isinstance(parent, SpectrumDataTreeItem):
            return

        if mask is not None and np.all([x for x in mask]):
            return

        if mask is None:
            spec_data = parent.item
            mask = np.zeros(spec_data.x.shape, dtype=bool)

        layer_data_item = LayerDataTreeItem(parent, mask, rois,
                                            "Layer {}".format(
                                                parent.rowCount()+1))
        layer_data_item.setIcon(QtGui.QIcon(path.join(PATH, 'layer.png')))

        parent.add_layer(layer_data_item)
        parent.appendRow(layer_data_item)

        self.sig_added_item.emit(layer_data_item.index())

        return layer_data_item

    def create_fit_model(self, parent, model_name):
        if not isinstance(parent, LayerDataTreeItem):
            return

        try:
            model = model_fitting.get_model(model_name)
        except TypeError:
            print("Current model is not implemented.")
            return

        parent.add_model(model)
        model_data_item = ModelDataTreeItem(parent, model, model_name)
        model_data_item.setIcon(QtGui.QIcon(path.join(PATH, 'model.png')))

        parent.appendRow(model_data_item)
        self.sig_added_item.emit(model_data_item.index())
        self.sig_added_fit_model.emit(model_data_item)

    # --- overridden functions
    def setData(self, index, value, role=QtCore.Qt.EditRole):
        item = self.itemFromIndex(index)
        if role == QtCore.Qt.EditRole:
            if isinstance(item, ParameterDataTreeItem):
                value = float_check(value)
                if value:
                    item.setData(value)
                    item.setText(str(value))
            else:
                item.setData(value)
                item.setText(str(value))

            self.dataChanged.emit(index, index)
            return True

        elif role == QtCore.Qt.CheckStateRole:
            item.setData(value, role=QtCore.Qt.CheckStateRole)

            self.dataChanged.emit(index, index)
            return True

        return False

    def hasChildren(self, parent_index=None, *args, **kwargs):
        # if parent_index is not None and self.itemFromIndex(parent_index):
        #     item = self.itemFromIndex(parent_index)
        #
        #     if isinstance(item, LayerDataTreeItem):
        #         return False

        return super(SpectrumDataTreeModel, self).hasChildren(parent_index,
                                                              *args, **kwargs)

    def rowCount(self, parent_index=None, *args, **kwargs):
        # if parent_index is not None and self.itemFromIndex(parent_index):
        #     item = self.itemFromIndex(parent_index)
        #
        #     if isinstance(item, LayerDataTreeItem):
        #         return 0

        return super(SpectrumDataTreeModel, self).rowCount(parent_index,
                                                           *args, **kwargs)

    # Subclasses to expose Data, Fits, and any other deeply
    # embedded information
    class Collections(object):
        """Provide direct access to embedded information."""
        def __init__(self, model):
            self._model = model

        # --- Make iterable, over both data and layers.
        def __iter__(self):
            raise NotImplementedError('__iter__ must be implemented in a subclass.')

        def __len__(self):
            return sum(1 for _ in self)

        def __getitem__(self, key):
            for (existing_key, value) in self:
                if key == existing_key:
                    return value
            raise KeyError('Key "{}" does not exist.'.format(key))

    class DataCollection(Collections):
        """Provide direct access to all the data in the tree."""
        def __iter__(self):
            for data_item in self._model.items:
                yield (clean_special(data_item.text()), data_item.item)
                for layer_item in data_item.layers:
                    yield(clean_special(layer_item.text()), layer_item.item)

    class FitCollection(Collections):
        """Provide direct access to all the fits in the tree."""
        def __iter__(self):
            for data_item in self._model.items:
                for layer_item in data_item.layers:
                    models = layer_item._models
                    if (len(models)):
                        yield(clean_special(layer_item.text()),
                              models)


def clean_special(text):
    """Remove special characters."""
    return text.replace(' ', '_')
