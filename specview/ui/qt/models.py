from PyQt4 import QtGui, QtCore, Qt
import numpy as np
from specview.analysis import model_fitting
import inspect
from items import (SpectrumDataTreeItem, ModelDataTreeItem, LayerDataTreeItem,
                   ParameterDataTreeItem)


class SpectrumDataTreeModel(QtGui.QStandardItemModel):
    """Custom TreeView model for displaying DataSetItems."""
    added_model = QtCore.pyqtSignal(ModelDataTreeItem)

    def __init__(self):
        super(SpectrumDataTreeModel, self).__init__()
        self._items = []

    def create_data(self, nddata, name=""):
        ds_item = SpectrumDataTreeItem(nddata, name)
        self.itemChanged.connect(self._item_changed)

        self._items.append(ds_item)
        self.appendRow(ds_item)

    def create_layer(self, parent, mask=None, rois=None, use_model=False):
        if not isinstance(parent, SpectrumDataTreeItem):
            raise TypeError("Expected type SpectrumDataTreeItem, "
                            "got {}".format(type(parent)))

        if mask is not None and all(x == False for x in mask):
            return

        if mask is None:
            spec_data = parent.item
            mask = np.zeros(spec_data.x.shape, dtype=bool)
        else:
            # Assuming that mask is actually a slice, we must invert the slice
            # to create a true mask.
            mask = np.logical_not(mask)

        layer_item = LayerDataTreeItem(parent, mask, rois)
        parent.add_layer(layer_item)
        parent.appendRow(layer_item)
        return layer_item

    def create_fit_model(self, parent, model_name):
        if not isinstance(parent, LayerDataTreeItem):
            raise TypeError("Expected type LayerDataTreeItem, "
                            "got {}".format(str(type(parent))))

        model = model_fitting.get_model(model_name)
        parent.add_model(model)
        model_item = ModelDataTreeItem(parent, model, model_name)
        parent.appendRow(model_item)

        self.added_model.emit(model_item)

    def _item_changed(self, item):
        if isinstance(item, ParameterDataTreeItem):
            item.parent.update_parameter(item._name,
                                         item.data().toPyObject())

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if role == QtCore.Qt.EditRole:
            print("HERE")
            item = self.itemFromIndex(index)
            # value = str(value.toPyObject())
            item.setData(value)
            item.setText(str(value.toPyObject()))
            self.dataChanged.emit(index, index)

            return True
        return False
