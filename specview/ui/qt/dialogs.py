from PyQt4 import QtGui
from astropy.io import fits
from astropy.io.fits.hdu.table import _TableLikeHDU as FITS_table


class FileEditDialog(QtGui.QDialog):
    def __init__(self, file_path, parent=None):
        super(FileEditDialog, self).__init__(parent)
        self.ext = None
        self.flux = None
        self.dispersion = None
        self.flux_unit = None
        self.dispersion_unit = None

        self.hdulist = fits.open(str(file_path))

        self.vb_layout_main = QtGui.QVBoxLayout()
        self.setLayout(self.vb_layout_main)

        self._setup_basic()

    def _setup_basic(self):
        # Form layout layout
        vb_layout = QtGui.QVBoxLayout()

        # Extension selector
        self.ext_selector = QtGui.QComboBox()
        self.ext_selector.addItems(["[{}] {}".format(i, self.hdulist[i].name)
                                    for i in range(len(self.hdulist))])
        self.ext_selector.currentIndexChanged.connect(self._set_selectors)

        # Manual units check box
        # self.manual_units_cb = QtGui.QCheckBox()
        # self.manual_units_cb.stateChanged.connect(self._on_checked)

        # Manual input lines
        self.man_flux_unit = QtGui.QLineEdit()
        self.man_disp_unit = QtGui.QLineEdit()

        # Flux and dispersion unit selectors, labels, and layouts
        # flux_hb_layout = QtGui.QHBoxLayout()
        # self.flux_unit_selector = QtGui.QComboBox()
        # self.flux_unit_label = QtGui.QLabel("Test")
        # self.flux_hb_layout = flux_hb_layout
        # self.flux_hb_layout.addWidget(self.flux_unit_selector)
        # self.flux_hb_layout.addWidget(self.flux_unit_label)
        #
        # disp_hb_layout = QtGui.QHBoxLayout()
        # self.disp_unit_selector = QtGui.QComboBox()
        # self.disp_unit_label = QtGui.QLabel("Test")
        # self.disp_hb_layout = disp_hb_layout
        # self.disp_hb_layout.addWidget(self.disp_unit_selector)
        # self.disp_hb_layout.addWidget(self.disp_unit_label)
        #
        # self._set_selectors(0)
        #
        # self.flux_unit_selector.currentIndexChanged.connect(self._set_labels)
        # self.disp_unit_selector.currentIndexChanged.connect(self._set_labels)

        # Label detailing how many extensions were found
        hdu_count = QtGui.QLabel("Detected {} extensions in this FITS "
                                 "file.".format(len(self.hdulist)))

        # Form layout
        self.form_layout = QtGui.QFormLayout()
        self.form_layout.addRow(self.tr("Extension"), self.ext_selector)
        # self.form_layout.addRow(self.tr("Manual Units"), self.manual_units_cb)
        self.form_layout.addRow(self.tr("Flux Unit"), self.man_flux_unit)
        self.form_layout.addRow(self.tr("Dispersion Unit"), self.man_disp_unit)

        # Accept button
        btn_accept = QtGui.QPushButton("&Accept")
        btn_accept.clicked.connect(self._on_accept)

        # Add widgets to form layout
        vb_layout.addWidget(hdu_count)
        vb_layout.addLayout(self.form_layout)

        # Create group box
        group_box = QtGui.QGroupBox("File Input Factory")
        group_box.setLayout(vb_layout)

        # Add form layout and accept button to main layout
        self.vb_layout_main.addWidget(group_box)
        self.vb_layout_main.addWidget(btn_accept)

    def _set_selectors(self, index):
        pass
        # if not self.manual_units_cb.isChecked():
        #     self.flux_unit_selector.clear()
        #     self.disp_unit_selector.clear()
        #     self.flux_unit_selector.addItems(
        #         self.hdulist[index].header.keys())
        #     self.disp_unit_selector.addItems(
        #         self.hdulist[index].header.keys())
        #
        #     self._set_labels()

    def _set_labels(self):
        index = self.ext_selector.currentIndex()
        header = self.hdulist[index].header
        flux_key = str(self.flux_unit_selector.currentText())
        disp_key = str(self.disp_unit_selector.currentText())

        if flux_key in header.keys():
            self.flux_unit_label.setText(str(header[flux_key])[:20])
        else:
            self.flux_unit_label.setText("")

        if disp_key in header.keys():
            self.disp_unit_label.setText(str(header[disp_key])[:20])
        else:
            self.disp_unit_label.setText("")

    def _on_accept(self):
        self.ext = int(self.ext_selector.currentIndex())
        if isinstance(self.hdulist[self.ext], FITS_table):
            self.flux = self.hdulist[self.ext].data.names[1]
            self.dispersion = self.hdulist[self.ext].data.names[0]

        # self.flux_unit = str(self.hdulist[self.ext].header[
        #     str(self.flux_unit_selector.currentText())]).lower()
        self.flux_unit = str(self.man_flux_unit.text())
        # self.dispersion_unit = str(self.hdulist[self.ext].header[
        #     str(self.disp_unit_selector.currentText())]).lower()
        self.disp_unit = str(self.man_disp_unit.text())

        super(FileEditDialog, self).accept()
