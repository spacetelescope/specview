# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'spectrum_view.ui'
#
# Created: Thu Jan 29 21:39:11 2015
#      by: PyQt4 UI code generator 4.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_mainView(object):
    def setupUi(self, mainView):
        mainView.setObjectName(_fromUtf8("mainView"))
        mainView.resize(750, 374)
        self.gridLayout = QtGui.QGridLayout(mainView)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.plotView = MatplotlibWidget(mainView)
        self.plotView.setObjectName(_fromUtf8("plotView"))
        self.gridLayout.addWidget(self.plotView, 0, 0, 1, 1)
        self.spectraListView = QtGui.QListView(mainView)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.spectraListView.sizePolicy().hasHeightForWidth())
        self.spectraListView.setSizePolicy(sizePolicy)
        self.spectraListView.setObjectName(_fromUtf8("spectraListView"))
        self.gridLayout.addWidget(self.spectraListView, 0, 1, 1, 1)

        self.retranslateUi(mainView)
        QtCore.QMetaObject.connectSlotsByName(mainView)

    def retranslateUi(self, mainView):
        mainView.setWindowTitle(_translate("mainView", "Spectrum Viewer", None))

from specview.proto.specviewer.mplwidget import MatplotlibWidget
