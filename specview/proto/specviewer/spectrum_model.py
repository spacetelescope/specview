'''Model for displaying Spectra data in the Gui.
'''
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QStandardItem, QStandardItemModel

from specview.proto.specviewer.debug import msg_debug


class SpectrumDataModel(QStandardItemModel):
    def __init__(self, spectra, parent=None):
        super(SpectrumDataModel, self).__init__(parent=parent)
        self.setHorizontalHeaderLabels(['Spectra'])

        for spectrum in spectra:
            self.appendRow(spectrum)

    def add(self, spectrum):
        self.appendRow(spectrum)

    def remove(self, name):
        item = self.findItems(name)[0]
        self.takeRow(item.row())

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
            data = data.meta['name']
        except (AttributeError, KeyError):
            pass
        super(SpectrumItem, self).setData(data, role)
