from PyQt4 import QtGui, QtCore, Qt


class MenuBar(QtGui.QMenuBar):
    def __init__(self):
        super(MenuBar, self).__init__()
        # File
        self.exit_action = QtGui.QAction('&Exit', self)
        self.exit_action.setShortcut('Ctrl+Q')
        self.exit_action.setStatusTip('Exit application')

        self.open_action = QtGui.QAction('&Open', self)
        self.open_action.setShortcut('Ctrl+O')
        self.open_action.setStatusTip('Open file')

        # Plotting
        self.img_plot_action = QtGui.QAction('&Image', self)
        self.img_plot_action.setToolTip('Plot 2D image from data')

        self.spec_plot_action = QtGui.QAction('&Spectrum', self)
        self.spec_plot_action.setToolTip('Plot 1D spectrum from data or ROI')

        # Windows
        self.action_toggle_console = QtGui.QAction('&Console', self)
        self.action_toggle_console.setToolTip('Toggle console dock.')

        self.action_toggle_data_view = QtGui.QAction('&Data Sets', self)
        self.action_toggle_data_view.setToolTip('Toggle data set dock.')

        self.action_toggle_info_view = QtGui.QAction('&Info View', self)
        self.action_toggle_info_view.setToolTip('Toggle info view dock.')

        # Tools
        file_menu = self.addMenu('&File')
        file_menu.addAction(self.open_action)
        file_menu.addAction(self.exit_action)

        plot_menu = self.addMenu('&Plot')
        plot_menu.addAction(self.img_plot_action)
        plot_menu.addAction(self.spec_plot_action)

        self.docks_menu = self.addMenu('&Docks')