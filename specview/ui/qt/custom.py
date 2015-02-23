from PyQt4 import QtGui, QtCore, Qt
from astropy.units import Unit
from astropy.modeling import models
import numpy as np
from specview.io import read_data


class SpecViewItem(QtGui.QStandardItem):
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
    def __init__(self, item=None, name="Data"):
        super(SpecViewItem, self).__init__()

        self.setEditable(True)
        self._item = item
        self._model_views = []
        self.setText(name)
        self.setData(item)

    @property
    def item(self):
        return self._item

    @property
    def models(self):
        return self._model_views
        # return self._item.models

    def add_model(self, model):
        self._model_views.append(model)
        # self._item.add_model(model)

    def remove_model(self, model):
        self._model_views.remove(model)
        # self._item.remove_model(model)


class SpecViewModel(QtGui.QStandardItemModel):
    """
    Custom TreeView model for displaying DataSetItems.
    """
    def __init__(self):
        super(SpecViewModel, self).__init__()
        self._items = []

    def add_row(self, item):
        if not isinstance(item, SpecViewItem):
            item = SpecViewItem(item)

        self._items.append(item)
        self.appendRow(item)


class ModelViewItem(QtGui.QStandardItem):
    """
    Temporary class. This should be coupled with SpecViewItem as one
    object. This will change in the future.
    """
    def __init__(self, model=None, parent=None, name="Model"):
        super(SpecViewItem, self).__init__()

        self.setEditable(True)
        self._item = parent
        self._model = model


class ModelViewModel(QtGui.QStandardItemModel):
    """
    Temporary class. This should be coupled with SpecViewModel as one object.
    This will be changed in the future.
    """
    def __init__(self):
        super(ModelViewModel, self).__init__()
        self._models = []

    def add_row(self, model):
        if not isinstance(model, ModelViewModel):
            model = ModelViewModel(model)

        self._models.append(model)
        self.appendRow(model)


