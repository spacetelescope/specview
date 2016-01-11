from os import path, sys
import numpy as np

from astropy.modeling import Fittable1DModel

from ..external.qt import QtGui, QtCore

from ..analysis import model_fitting
from ..tools import model_registry
from ..ui.items import (CubeDataTreeItem, SpectrumDataTreeItem,
                        ModelDataTreeItem, LayerDataTreeItem,
                        ParameterDataTreeItem, AttributeValueDataTreeItem,
                        float_check)

PATH = path.join(path.dirname(sys.modules[__name__].__file__), "qt", "img")


class DataTreeModel(QtGui.QStandardItemModel):
    """Custom TreeView model for displaying DataSetItems."""
    sig_added_item = QtCore.Signal(QtCore.QModelIndex)
    sig_added_fit_model = QtCore.Signal(ModelDataTreeItem)
    sig_removed_item = QtCore.Signal(object)
    sig_set_visibility = QtCore.Signal(LayerDataTreeItem, bool)

    def __init__(self):
        super(DataTreeModel, self).__init__()
        self._items = []
        self.itemChanged.connect(self._item_changed)
        self.check_col = 1

    @property
    def items(self):
        return self._items

    @property
    def data_items(self):
        return [x.item for x in self._items]

    @staticmethod
    def _item_changed(item):
        if isinstance(item, AttributeValueDataTreeItem):
            item.parent.parent.update_parameter(item._name, item.data(), parent_parameter_name=item.parent._name)

        elif isinstance(item, ParameterDataTreeItem):
            if hasattr(item.parent, 'update_parameter'):
                item.parent.update_parameter(item._name, item.data())

    def remove_data_item(self, index, parent_index):
        item = index.model().itemFromIndex(index)
        success = self.removeRow(index.row(), parent_index)
        print("Removing item {}, {}, {}, {}".format(success, index,
                                                    parent_index, item))
        # if it's data
        if item in self._items:
            self._items.remove(item)

        # if it's a layer
        for data in self._items:
            data.remove_layer(item)

        # if it's a model
        for data in self._items:
            for layer in data.layers:
                print("It's a model, removing")
                layer.remove_model(item)
                if isinstance(item.model, Fittable1DModel):
                    # for now, emit signal just when an astropy model is being removed.
                    self.sig_removed_item.emit(item)

    def create_spec_data_item(self, nddata, name="Spectrum Data"):
        spec_data_item = SpectrumDataTreeItem(nddata, name)
        spec_data_item.setIcon(QtGui.QIcon(path.join(PATH, 'data_set.png')))

        self._items.append(spec_data_item)
        self.appendRow(spec_data_item)
        self.sig_added_item.emit(spec_data_item.index())

        return spec_data_item

    def create_cube_data_item(self, nddata, name="Cube Data"):
        cube_data_item = CubeDataTreeItem(nddata, name)
        cube_data_item.setIcon(QtGui.QIcon(path.join(PATH, 'data_set.png')))

        self._items.append(cube_data_item)
        self.appendRow(cube_data_item)
        self.sig_added_item.emit(cube_data_item.index())

        return cube_data_item

    def create_layer_item(self, parent, node_parent=None, filter_mask=None,
                          rois=None, collapse=None, name=None):
        if filter_mask is None:
            parent_item = parent.item
            filter_mask = np.ones(parent_item.shape, dtype=bool)

        if name is None:
            name = "Layer {}".format(parent.rowCount()+1)

        layer_data_item = LayerDataTreeItem(parent, filter_mask, rois=rois,
                                            collapse=collapse, name=name,
                                            node_parent=node_parent)
        layer_data_item.setIcon(QtGui.QIcon(path.join(PATH, 'layer.png')))

        if node_parent is not None:
            node_parent.add_layer_item(layer_data_item)
            node_parent.appendRow(layer_data_item)
        else:
            parent.add_layer_item(layer_data_item)
            parent.appendRow(layer_data_item)

        self.sig_added_item.emit(layer_data_item.index())

        return layer_data_item

    def create_fit_model(self, parent, editor, model_name):
        if not isinstance(parent, LayerDataTreeItem):
            return

        try:
            model = model_fitting.get_model(model_name)
        except TypeError:
            print("Model {} is not implemented.".format(model_name))
            return

        model_data_item = ModelDataTreeItem(parent, model, model_name)
        parent.add_model_item(model_data_item)
        model_data_item.setIcon(QtGui.QIcon(path.join(PATH, 'model.png')))

        parent.appendRow(model_data_item)
        self.sig_added_item.emit(model_data_item.index())
        self.sig_added_fit_model.emit(model_data_item)

        self.updateModelExpression(editor, parent)

    # Temporarily put this in here. It probably belongs somewhere else,
    # but for now we need it to just populate the expression text field.
    def updateModelExpression(self, editor, parent):
        components = []
        for c in parent._model_items:
            components.append(c._model)

        #TODO  when reading from file, parent.model contains a CompoundModel. Use it to derive expression.
        #TODO  when adding 1st component, parent.model contains a component. Expression is empty.
        #TODO  when adding subsequent components, parent.model contains a CompoundModel. Derive expression as above.

        compound_model = model_registry.buildSummedCompoundModel(components)
        if editor:
            editor.expression_field.setText("")
            if hasattr(compound_model, '_format_expression'):
                expression = compound_model._format_expression()
                editor.expression_field.setText(expression)

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if role == QtCore.Qt.EditRole:
            item = self.itemFromIndex(index)
            item.setData(value)

            if isinstance(item, ParameterDataTreeItem):
                validated_value = float_check(value)
                if validated_value:
                    item.setText(str(value))

            self.dataChanged.emit(index, index)

            return True
        elif role == QtCore.Qt.CheckStateRole:
            item = self.itemFromIndex(index)

            if not isinstance(item, LayerDataTreeItem):
                return False

            item.setCheckState(~item.checkState())
            self.sig_set_visibility.emit(item, item.checkState() ==
                                            QtCore.Qt.Checked)

        return False

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid():
            return None

        item = self.itemFromIndex(index)

        if role == QtCore.Qt.CheckStateRole and isinstance(item, LayerDataTreeItem):
            return int(QtCore.Qt.Checked if item.checkState() ==
                                            QtCore.Qt.Checked else
                       QtCore.Qt.Unchecked)

        return super(DataTreeModel, self).data(index, role)

    def hasChildren(self, parent_index=QtCore.QModelIndex(), *args, **kwargs):
        # if parent_index is not None and self.itemFromIndex(parent_index):
        #     item = self.itemFromIndex(parent_index)
        #
        #     if isinstance(item, LayerDataTreeItem):
        #         return False

        return super(DataTreeModel, self).hasChildren(parent_index, *args,
                                                      **kwargs)

    def rowCount(self, parent_index=QtCore.QModelIndex(), *args, **kwargs):
        # if parent_index is not None and self.itemFromIndex(parent_index):
        #     item = self.itemFromIndex(parent_index)
        #
        #     if isinstance(item, LayerDataTreeItem):
        #         return 0

        return super(DataTreeModel, self).rowCount(parent_index, *args,
                                                   **kwargs)
