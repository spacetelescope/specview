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

        ext_layout = QtGui.QHBoxLayout()
        ext_layout.addWidget(QtGui.QLabel("Extension"))
        ext_layout.addWidget(self.ext_selector)
        ext_layout.addWidget(self.flux_col_selector)
        ext_layout.addWidget(self.man_flux_unit)

        # Form layout
        self.form_layout = QtGui.QVBoxLayout()
        self.form_layout.addLayout(ext_layout)
        # self.form_layout.addRow(self.tr("Flux Column"), self.flux_col_selector)
        # self.form_layout.addRow(self.tr("Dispersion Column"),
        #                         self.disp_col_selector)
        # self.form_layout.addRow(self.tr("Flux Unit"), self.man_flux_unit)
        # self.form_layout.addRow(self.tr("Dispersion Unit"), self.man_disp_unit)

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


class TopAxisDialog(QtGui.QDialog):
    def __init__(self, parent=None):
        super(TopAxisDialog, self).__init__(parent)
        self.ref_wave = 0.0
        self.redshift = 0.0

        self.vb_layout_main = QtGui.QVBoxLayout()
        self.setLayout(self.vb_layout_main)

        self._container_list = []

        self.wgt_display_axis = QtGui.QComboBox()
        self.wgt_display_axis.addItems(["Redshifted Wavelength", "Velocity",
                                        "Channel"])
        self.wgt_display_axis.currentIndexChanged.connect(self._on_select)

        frm_select = QtGui.QFormLayout()
        frm_select.addRow("Display axis:", self.wgt_display_axis)

        # Redshift parameters
        self.grp_redshift = QtGui.QGroupBox("Redshift Parameters")
        self.wgt_redshift = QtGui.QLineEdit()
        self.wgt_redshift.setValidator(QtGui.QDoubleValidator())
        frm_redshift = QtGui.QFormLayout()
        self.grp_redshift.setLayout(frm_redshift)
        frm_redshift.addRow("Amount:", self.wgt_redshift)
        self._container_list.append(self.grp_redshift)

        # Velocity parameters
        self.grp_vel = QtGui.QGroupBox("Velocity Parameters")
        self.wgt_ref_wave_unit = QtGui.QLabel("")
        self.wgt_ref_wave = QtGui.QLineEdit()
        hb_ref_wave = QtGui.QHBoxLayout()
        hb_ref_wave.addWidget(self.wgt_ref_wave)
        hb_ref_wave.addWidget(self.wgt_ref_wave_unit)
        self.wgt_ref_wave.setValidator(QtGui.QDoubleValidator())
        frm_vel = QtGui.QFormLayout()
        self.grp_vel.setLayout(frm_vel)
        frm_vel.addRow("Reference Wavelength:", hb_ref_wave)
        self._container_list.append(self.grp_vel)

        button_box = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok |
                                            QtGui.QDialogButtonBox.Cancel)
        button_box.accepted.connect(self._on_accept)
        button_box.rejected.connect(self._on_reject)

        self.vb_layout_main.addLayout(frm_select)
        self.vb_layout_main.addWidget(self.grp_redshift)
        self.vb_layout_main.addWidget(self.grp_vel)
        self.vb_layout_main.addWidget(button_box)

        self._on_select(0)

    def set_current_unit(self, unit):
        self.wgt_ref_wave_unit.setText(unit)

    def _on_select(self, index):
        for cntr in self._container_list:
            cntr.hide()

        if index < len(self._container_list):
            self._container_list[index].show()

    def _on_accept(self):
        self.mode = self.wgt_display_axis.currentIndex()

        rw_val = str(self.wgt_ref_wave.text())
        self.ref_wave = float(rw_val) if rw_val != '' else self.ref_wave
        rs = str(self.wgt_redshift.text())
        self.redshift = float(rs) if rs != '' else self.redshift

        super(TopAxisDialog, self).accept()

    def _on_reject(self):
        super(TopAxisDialog, self).reject()


