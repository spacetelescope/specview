from os import path, sys
from PyQt4 import QtGui, QtCore
import numpy as np

from specview.analysis import model_fitting
from specview.ui.qt.tree_items import (SpectrumDataTreeItem, ModelDataTreeItem,
                     LayerDataTreeItem, ParameterDataTreeItem)

PATH = path.join(path.dirname(sys.modules[__name__].__file__), "qt", "img")


class SpectrumDataTreeModel(QtGui.QStandardItemModel):
    """Custom TreeView model for displaying DataSetItems."""
    sig_added_item = QtCore.pyqtSignal(QtCore.QModelIndex)
    sig_added_fit_model = QtCore.pyqtSignal(ModelDataTreeItem)
    sig_removed_item = QtCore.pyqtSignal(object)

    def __init__(self):
        super(SpectrumDataTreeModel, self).__init__()
        self._items = []
        self.itemChanged.connect(self._item_changed)

    @property
    def items(self):
        return self._items

    @property
    def data_items(self):
        return [x.item for x in self._items]

    # --- protected functions
    def _item_changed(self, item):
        if isinstance(item, ParameterDataTreeItem):
            item.parent.update_parameter(item._name,
                                         item.data().toPyObject())

    # --- public functions
    def remove_data_item(self, index, parent_index):
        item = index.model().itemFromIndex(index)
        self.removeRow(index.row(), parent_index)

        if item in self._items:
            self._items.remove(item)

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