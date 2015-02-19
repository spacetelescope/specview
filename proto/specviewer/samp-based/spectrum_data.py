'''Spectrum Data Model
'''
import logging
from debug import msg_debug

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QStandardItem, QStandardItemModel

from astropy.nddata import NDData

class SpectrumData(NDData):
    def __init__(self, id, array):
        self.id = id
        super(SpectrumData, self).__init__(array)

class SpectrumDataStore(list):
    pass


class SpectrumDataModel(QStandardItemModel):
    def __init__(self, spectra, parent=None):
        super(SpectrumDataModel, self).__init__(parent=parent)
        self.setHorizontalHeaderLabels(['Spectra'])

        for spectrum in spectra:
            self.appendRow(spectrum)

    def appendRow(self, spectrum):
        super(SpectrumDataModel, self).appendRow(SpectrumItem(spectrum=spectrum))


class SpectrumItem(QStandardItem):
    def __init__(self, spectrum=None):
        msg_debug('entered.')
        super(SpectrumItem, self).__init__()
        if spectrum is not None:
            self.setData(spectrum)

    def setData(self, data, role=Qt.DisplayRole):
        try:
            data = data.id
        except AttributeError:
            pass
        super(SpectrumItem, self).setData(data, role)
