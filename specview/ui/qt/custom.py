from PyQt4 import QtGui, QtCore, Qt
from astropy.units import Unit
from astropy.modeling import models
import numpy as np
from specview.io import read_data


class SpecViewItem(QtGui.QStandardItem):
    """
    Subclasses QStandarditem; provides the base class for all items listed
    in the data set tree view.
    """
    def __init__(self, item=None):
        super(SpecViewItem, self).__init__()

        self.setEditable(True)
        self._item = item
        self.setText("Data")
        self.setData(item)

    @property
    def item(self):
        return self._item


class SpecViewModel(QtGui.QStandardItemModel):
    """
    Custom TreeView model for displaying DataSetItems.
    """
    def __init__(self):
        super(SpecViewModel, self).__init__()
        self._items = []

        self.appendRow(SpecViewItem(read_data("/Users/nearl/Downloads/3500_00_m05p00.ms.fits")))
        self.appendRow(SpecViewItem(read_data("/Users/nearl/Downloads/3500_00_m05p00.ms.fits")))
        self.appendRow(SpecViewItem(read_data("/Users/nearl/Downloads/3500_00_m05p00.ms.fits")))
        self.appendRow(SpecViewItem(read_data("/Users/nearl/Downloads/3500_00_m05p00.ms.fits")))
        self.appendRow(SpecViewItem(read_data("/Users/nearl/Downloads/3500_00_m05p00.ms.fits")))

    def add_row(self, item):
        self._items.append(item)
        self.appendRow(item)


