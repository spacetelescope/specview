from PyQt4 import QtGui, QtCore, Qt
import numpy as np
from specview.analysis import model_fitting
import inspect
from qt.tree_items import (SpectrumDataTreeItem, ModelDataTreeItem,
                     LayerDataTreeItem, ParameterDataTreeItem)


class SpectrumDataTreeModel(QtGui.QStandardItemModel):
    """Custom TreeView model for displaying DataSetItems."""
    added_model = QtCore.pyqtSignal(ModelDataTreeItem)


    def __init__(self):
        super(SpectrumDataTreeModel, self).__init__()
        self._items = []
        self.itemChanged.connect(self._item_changed)

    # --- protected functions
    def _item_changed(self, item):
        if isinstance(item, ParameterDataTreeItem):
            item.parent.update_parameter(item._name,
                                         item.data().toPyObject())

    # --- public functions
    def create_data_item(self, nddata, name=""):
        ds_item = SpectrumDataTreeItem(nddata, name)
        self._items.append(ds_item)
        self.appendRow(ds_item)
        return ds_item

    def create_layer(self, parent, mask=None, rois=None):
        if not isinstance(parent, SpectrumDataTreeItem):
            raise TypeError("Expected type SpectrumDataTreeItem, "
                            "got {}".format(type(parent)))

        if mask is not None and np.all([x for x in mask]):
            return

        if mask is None:
            print("Creating mask")
            spec_data = parent.item
            mask = np.zeros(spec_data.x.shape, dtype=bool)
        print(parent.item.x.shape, parent.item.y.shape)
        print(mask.shape)
        layer_data_item = LayerDataTreeItem(parent, mask, rois,
                                            "Layer ({})".format(parent.text()))
        parent.add_layer(layer_data_item)
        parent.appendRow(layer_data_item)

        return layer_data_item

    def create_fit_model(self, parent, model_name):
        if not isinstance(parent, LayerDataTreeItem):
            raise TypeError("Expected type LayerDataTreeItem, "
                            "got {}".format(str(type(parent))))

        model = model_fitting.get_model(model_name)
        parent.add_model(model)
        model_item = ModelDataTreeItem(parent, model, model_name)
        parent.appendRow(model_item)

        self.added_model.emit(model_item)

    # --- overridden functions
    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if role == QtCore.Qt.EditRole:
            item = self.itemFromIndex(index)
            item.setData(value)
            item.setText(str(value.toPyObject()))

            # TODO: insert check to make sure value actually is a float
            if isinstance(item, ParameterDataTreeItem):
                item.setText(str(float(str(value.toPyObject()))))

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