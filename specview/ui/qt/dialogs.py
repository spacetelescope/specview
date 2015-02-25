from PyQt4 import QtGui, QtCore
from astropy.io import fits


class FileEditDialog(QtGui.QDialog):
    def __init__(self, file_path, parent=None):
        super(FileEditDialog, self).__init__(parent)

        hdu_list = fits.open(str(file_path))

        vb_layout = QtGui.QVBoxLayout()
        self.setLayout(vb_layout)

        ext_selector = QtGui.QComboBox()
        ext_selector.addItems(["{}".format(i) for i in range(len(
            hdu_list))])

        self.flux_unit_selector = QtGui.QComboBox()
        self.flux_unit_selector.addItems(hdu_list[0].header.keys())

        self.disp_unit_selector = QtGui.QComboBox()
        self.disp_unit_selector.addItems(hdu_list[0].header.keys())

        label = QtGui.QLabel("File Input Factory")
        hdu_count = QtGui.QLabel("Detected {} extensions in this FITs "
                                 "file.".format(len(hdu_list)))

        form_layout = QtGui.QFormLayout()
        form_layout.addRow(self.tr("&Extension"), ext_selector)
        form_layout.addRow(self.tr("&Flux Unit"), self.flux_unit_selector)
        form_layout.addRow(self.tr("&Dispersion Unit"), self.disp_unit_selector)

        vb_layout.addWidget(label)
        vb_layout.addWidget(hdu_count)
        vb_layout.addLayout(form_layout)

