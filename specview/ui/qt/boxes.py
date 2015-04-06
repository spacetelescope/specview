from ...external.qt import QtGui, QtCore


class StatisticsGroupBox(QtGui.QGroupBox):
    def __init__(self, title="", parent=None):
        super(StatisticsGroupBox, self).__init__(title, parent)

        self.lbl_mean = QtGui.QLabel()
        self.lbl_median = QtGui.QLabel()
        self.lbl_stddev = QtGui.QLabel()
        self.lbl_total = QtGui.QLabel()

        stat_form_layout = QtGui.QFormLayout()
        stat_form_layout.addRow(self.tr("Mean:"), self.lbl_mean)
        stat_form_layout.addRow(self.tr("Median:"), self.lbl_median)
        stat_form_layout.addRow(self.tr("Std. Dev.:"), self.lbl_stddev)
        stat_form_layout.addRow(self.tr("Total:"), self.lbl_total)

        self.setLayout(stat_form_layout)

    def set_labels(self, stats):
        self.lbl_mean.setText(str(stats['mean']))
        self.lbl_median.setText(str(stats['median']))
        self.lbl_stddev.setText(str(stats['stddev']))
        self.lbl_total.setText(str(stats['total']))
