from specview.external.qt import QtGui, QtCore
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

        # Manual input lines
        self.man_flux_unit = QtGui.QLineEdit()
        self.man_disp_unit = QtGui.QLineEdit()

        # Column name selectors
        self.flux_col_selector = QtGui.QComboBox()
        self.disp_col_selector = QtGui.QComboBox()

        # Label detailing how many extensions were found
        hdu_count = QtGui.QLabel("Detected {} extensions in this FITS "
                                 "file.".format(len(self.hdulist)))

        # Form layout
        self.form_layout = QtGui.QFormLayout()
        self.form_layout.addRow(self.tr("Extension"), self.ext_selector)
        self.form_layout.addRow(self.tr("Flux Column"), self.flux_col_selector)
        self.form_layout.addRow(self.tr("Dispersion Column"),
                                self.disp_col_selector)
        self.form_layout.addRow(self.tr("Flux Unit"), self.man_flux_unit)
        self.form_layout.addRow(self.tr("Dispersion Unit"), self.man_disp_unit)

        # Add widgets to form layout
        vb_layout.addWidget(hdu_count)
        vb_layout.addLayout(self.form_layout)

        # Create group box
        group_box = QtGui.QGroupBox("File Input Factory")
        group_box.setLayout(vb_layout)

        # Add form layout and accept button to main layout
        self.vb_layout_main.addWidget(group_box)
        # self.vb_layout_main.addWidget(btn_accept)
        button_box = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok |
                                            QtGui.QDialogButtonBox.Cancel)
        button_box.accepted.connect(self._on_accept)
        button_box.rejected.connect(self._on_reject)

        self.vb_layout_main.addWidget(button_box)

    def _set_selectors(self, index):
        self.flux_col_selector.clear()
        self.disp_col_selector.clear()

        data = self.hdulist[index].data

        if data is not None:
            col_names = data.names
        else:
            col_names = ""

        self.flux_col_selector.addItems(col_names)
        self.disp_col_selector.addItems(col_names)

    def _on_accept(self):
        self.ext = int(self.ext_selector.currentIndex())

        if isinstance(self.hdulist[self.ext], FITS_table):
            flux_ind = self.flux_col_selector.currentIndex()
            disp_ind = self.disp_col_selector.currentIndex()
            self.flux = self.hdulist[self.ext].data.names[flux_ind]
            self.dispersion = self.hdulist[self.ext].data.names[disp_ind]

        self.flux_unit = str(self.man_flux_unit.text())
        self.disp_unit = str(self.man_disp_unit.text())

        super(FileEditDialog, self).accept()

    def _on_reject(self):
        super(FileEditDialog, self).reject()


class PlotUnitsDialog(QtGui.QDialog):
    def __init__(self, parent=None):
        super(PlotUnitsDialog, self).__init__(parent)

        self.vb_layout_main = QtGui.QVBoxLayout()
        self.setLayout(self.vb_layout_main)

        self.wgt_flux_unit = None
        self.wgt_disp_unit = None

        self._setup_basic()

    def _setup_basic(self):
        self.wgt_flux_unit = QtGui.QLineEdit()
        self.wgt_disp_unit = QtGui.QLineEdit()

        form_layout = QtGui.QFormLayout()
        form_layout.addRow(self.tr("&Flux Unit:"), self.wgt_flux_unit)
        form_layout.addRow(self.tr("&Dispersion Unit:"), self.wgt_disp_unit)

        button_box = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok |
                                            QtGui.QDialogButtonBox.Cancel)
        button_box.accepted.connect(self._on_accept)
        button_box.rejected.connect(self._on_reject)

        self.vb_layout_main.addLayout(form_layout)
        self.vb_layout_main.addWidget(button_box)

    def _on_accept(self):
        self.flux_unit = str(self.wgt_flux_unit.text())
        self.disp_unit = str(self.wgt_disp_unit.text())

        super(PlotUnitsDialog, self).accept()

    def _on_reject(self):
        super(PlotUnitsDialog, self).reject()
