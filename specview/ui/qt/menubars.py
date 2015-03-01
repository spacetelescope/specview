from PyQt4 import QtGui


class MainMainBar(QtGui.QMenuBar):
    def __init__(self):
        super(MainMainBar, self).__init__()
        # File
        self.atn_exit = QtGui.QAction('&Exit', self)
        self.atn_exit.setShortcut('Ctrl+Q')
        self.atn_exit.setStatusTip('Exit application')

        self.atn_open = QtGui.QAction('&Open', self)
        self.atn_open.setShortcut('Ctrl+O')
        self.atn_open.setStatusTip('Open file')

        # File
        file_menu = self.addMenu('&File')
        file_menu.addAction(self.atn_open)
        file_menu.addAction(self.atn_exit)

        self.window_menu = self.addMenu('&Windows')