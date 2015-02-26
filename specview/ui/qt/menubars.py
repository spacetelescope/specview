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

        # Docks
        self.atn_toggle_console = QtGui.QAction('&Console', self)
        self.atn_toggle_console.setToolTip('Toggle console dock.')

        self.atn_toggle_data = QtGui.QAction('&Data Sets', self)
        self.atn_toggle_data.setToolTip('Toggle data set dock.')

        self.atn_toggle_info = QtGui.QAction('&Info View', self)
        self.atn_toggle_info.setToolTip('Toggle info view dock.')

        # File
        file_menu = self.addMenu('&File')
        file_menu.addAction(self.atn_open)
        file_menu.addAction(self.atn_exit)

        # Tools
        tool_menu = self.addMenu('&Tools')

        self.docks_menu = self.addMenu('&Docks')
        # self.docks_menu.addAction(self.atn_toggle_console)
        # self.docks_menu.addAction(self.atn_toggle_data)
        # self.docks_menu.addAction(self.atn_toggle_info)