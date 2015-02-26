from PyQt4 import QtGui, QtCore
import numpy as np

from specview.analysis import model_fitting
from specview.ui.qt.tree_items import (SpectrumDataTreeItem, ModelDataTreeItem,
                     LayerDataTreeItem, ParameterDataTreeItem)


class SpectrumDataTreeModel(QtGui.QStandardItemModel):
    """Custom TreeView model for displaying DataSetItems."""
    sig_added_item = QtCore.pyqtSignal(QtCore.QModelIndex)
    sig_added_fit_model = QtCore.pyqtSignal(ModelDataTreeItem)
    sig_removed_item = QtCore.pyqtSignal(object)

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
    def remove_data_item(self, index, parent_index):
        item = index.model().itemFromIndex(index)
        self.sig_removed_item.emit(item)
        self.removeRow(index.row(), parent_index)

    def create_data_item(self, nddata, name=""):
        spec_data_item = SpectrumDataTreeItem(nddata, name)
        self._items.append(spec_data_item)
        self.appendRow(spec_data_item)
        self.sig_added_item.emit(spec_data_item.index())

        return spec_data_item

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

        layer_data_item = LayerDataTreeItem(parent, mask, rois,
                                            "Layer {}".format(
                                                parent.rowCount()+1))
        parent.add_layer(layer_data_item)
        parent.appendRow(layer_data_item)
        self.sig_added_item.emit(layer_data_item.index())

        return layer_data_item

    def create_fit_model(self, parent, model_name):
        if not isinstance(parent, LayerDataTreeItem):
            raise TypeError("Expected type LayerDataTreeItem, "
                            "got {}".format(str(type(parent))))

        model = model_fitting.get_model(model_name)
        parent.add_model(model)
        model_data_item = ModelDataTreeItem(parent, model, model_name)

        parent.appendRow(model_data_item)
        self.sig_added_item.emit(model_data_item.index())
        self.sig_added_fit_model.emit(model_data_item)

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