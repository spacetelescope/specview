# from PySide import QtGui, QtCore
from ...external.qt import QtGui, QtCore
from os import sys, path
from .dialogs import PlotUnitsDialog, TopAxisDialog
from ..qt import resources

PATH = path.join(path.dirname(sys.modules[__name__].__file__), "img")


class BaseToolBar(QtGui.QToolBar):
    def __init__(self, parent=None):
        super(BaseToolBar, self).__init__(parent)
        self.setFloatable(False)
        self.setMovable(False)
        # self.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)

        self.atn_open_data = QtGui.QAction("&Insert \nROI", self)
        self.atn_open_data.setIcon(QtGui.QIcon(":/icons/open131.png"))
        self.atn_open_data.setToolTip('Add rectangular region-of-interest')

        self.atn_new_plot = QtGui.QAction("&New Plot", self)
        self.atn_new_plot.setIcon(QtGui.QIcon(":/icons/basic.png"))
        self.atn_new_plot.setToolTip('Create a new plot window')
        self.atn_new_plot.setDisabled(True)

        self.atn_add_plot = QtGui.QAction("&Add Plot", self)
        self.atn_add_plot.setIcon(QtGui.QIcon(":/icons/round62.png"))
        self.atn_add_plot.setToolTip('Add data to current plot window')
        self.atn_add_plot.setDisabled(True)

        self.atn_remove_plot = QtGui.QAction("&Remove Plot", self)
        self.atn_remove_plot.setIcon(QtGui.QIcon(":/icons/round60.png"))
        self.atn_remove_plot.setToolTip('Remove data from current plot window')
        self.atn_remove_plot.setDisabled(True)

        # Setup buttons
        self.addAction(self.atn_open_data)
        self.addSeparator()
        self.addAction(self.atn_new_plot)
        self.addAction(self.atn_add_plot)
        self.addAction(self.atn_remove_plot)

    @QtCore.Slot(bool, bool)
    def toggle_actions(self, data_selected, layer_selected):
        self.atn_new_plot.setDisabled(not (data_selected or not
        layer_selected))
        self.atn_add_plot.setDisabled(not layer_selected)
        self.atn_remove_plot.setDisabled(not layer_selected)


class SpectraToolBar(BaseToolBar):
    def __init__(self, parent=None):
        super(SpectraToolBar, self).__init__(parent)

        self.atn_insert_roi = QtGui.QAction("&Insert \nROI", self)
        self.atn_insert_roi.setIcon(QtGui.QIcon(":/icons/selection7.png"))
        self.atn_insert_roi.setToolTip('Add rectangular region-of-interest')

        self.atn_create_layer = QtGui.QAction("&Create Layer", self)
        self.atn_create_layer.setIcon(QtGui.QIcon(":/icons/add73.png"))
        self.atn_create_layer.setToolTip("Create new layer from ROIs")

        self.atn_measure = QtGui.QAction("&Measurements", self)
        self.atn_measure.setIcon(QtGui.QIcon(":/icons/add73.png"))
        self.atn_measure.setToolTip('Get measurements from current region')

        self.addAction(self.atn_measure)

        self.atn_equiv_width = QtGui.QAction("&Equivalent Width", self)
        self.atn_equiv_width.setIcon(QtGui.QIcon(":/icons/add73.png"))
        self.atn_equiv_width.setToolTip("Calculates equivalent width of the "
                                        "last two ROI regions")

        self.addAction(self.atn_equiv_width)

        self.addSeparator()

        self.atn_model_editor = QtGui.QAction("&Model Editor", self)
        self.atn_model_editor.setIcon(QtGui.QIcon(path.join(PATH,
                                                            "model_editor.png")))
        self.atn_model_editor.setToolTip('Opens the model editor')

        self.addAction(self.atn_model_editor)


class SpectraPlotToolBar(QtGui.QToolBar):
    def __init__(self, parent=None):
        super(SpectraPlotToolBar, self).__init__(parent)
        self.setContentsMargins(0, 0, 0, 0)

        self.atn_insert_roi = QtGui.QAction("&Insert \nROI", self)
        self.atn_insert_roi.setIcon(QtGui.QIcon(":/icons/selection7.png"))
        self.atn_insert_roi.setToolTip('Add rectangular region-of-interest')

        self.atn_create_layer = QtGui.QAction("&Create Layer", self)
        self.atn_create_layer.setIcon(QtGui.QIcon(":/icons/windows23.png"))
        self.atn_create_layer.setToolTip("Create new layer from ROIs")

        self.atn_measure = QtGui.QAction("&Measurements", self)
        self.atn_measure.setIcon(QtGui.QIcon(":/icons/info22.png"))
        self.atn_measure.setToolTip('Get measurements from current region')

        self.atn_equiv_width = QtGui.QAction("&Equivalent Width", self)
        self.atn_equiv_width.setIcon(QtGui.QIcon(":/icons/four37.png"))
        self.atn_equiv_width.setToolTip("Calculates equivalent width of the "
                                        "last two ROI regions")

        self.atn_model_editor = QtGui.QAction("&Model Editor", self)
        self.atn_model_editor.setIcon(QtGui.QIcon(":/icons/map29.png"))
        self.atn_model_editor.setToolTip('Opens the model editor')

        self.addAction(self.atn_insert_roi)
        self.addSeparator()
        self.addAction(self.atn_measure)
        self.addAction(self.atn_equiv_width)
        self.addAction(self.atn_model_editor)

        # ------

        self.unit_dialog = PlotUnitsDialog()
        self.top_axis_dialog = TopAxisDialog()

        plot_opt_menu = QtGui.QMenu()
        layer_opt_menu = QtGui.QMenu()

        # Plot options menu
        self.atn_edit_units = QtGui.QAction("&Change Units", self)
        self.atn_edit_units.setToolTip("Convert the plot units")
        self.atn_edit_units.triggered.connect(self._show_edit_units)

        self.atn_edit_top_axis = QtGui.QAction("Change Top Axis", self)
        self.atn_edit_top_axis.setToolTip("Display different top axis values")
        self.atn_edit_top_axis.triggered.connect(self._show_edit_top_axis)

        self.atn_toggle_errs = QtGui.QAction("Show Errors", self,
                                             checkable=True)
        self.atn_toggle_errs.setChecked(True)
        self.atn_toggle_errs.setToolTip("Toggle display of data uncertainty")

        plot_opt_menu.addAction(self.atn_toggle_errs)
        plot_opt_menu.addSeparator()
        plot_opt_menu.addAction(self.atn_edit_top_axis)
        plot_opt_menu.addAction(self.atn_edit_units)

        # Layer options menu
        self.atn_line_style = QtGui.QAction("&Line", self)
        self.atn_line_style.setToolTip("Render layer with line plot style")

        self.atn_hist_style = QtGui.QAction("&Histogram", self)
        self.atn_hist_style.setToolTip("Render layer in histogram style")

        self.atn_scat_style = QtGui.QAction("&Scatter", self)
        self.atn_scat_style.setToolTip("Render layer in scatter plot style")

        layer_opt_menu.addAction(self.atn_line_style)
        layer_opt_menu.addAction(self.atn_hist_style)
        layer_opt_menu.addAction(self.atn_scat_style)

        # Tool bar menu
        plot_opt_button = QtGui.QToolButton()
        plot_opt_button.setText("&Plot Options")
        plot_opt_button.setIcon(QtGui.QIcon(":/icons/open134.png"))
        plot_opt_button.setPopupMode(QtGui.QToolButton.InstantPopup)
        plot_opt_button.setMenu(plot_opt_menu)

        layer_opt_button = QtGui.QToolButton()
        layer_opt_button.setText("&Layer Options")
        layer_opt_button.setIcon(QtGui.QIcon(":/icons/document76.png"))
        layer_opt_button.setPopupMode(QtGui.QToolButton.InstantPopup)
        layer_opt_button.setMenu(layer_opt_menu)

        self.addSeparator()
        self.addWidget(plot_opt_button)
        self.addWidget(layer_opt_button)

    def _show_edit_units(self):
        self.unit_dialog.exec_()

    def _show_edit_top_axis(self):
        self.top_axis_dialog.exec_()


class ImageToolBar(BaseToolBar):
    def __init__(self):
        super(ImageToolBar, self).__init__()


class MOSToolBar(QtGui.QToolBar):
    def __init__(self, parent=None):
        super(MOSToolBar, self).__init__(parent)
        self.setFloatable(False)
        self.setMovable(False)

        self.atn_nav_right = QtGui.QAction("&Next Item", self)
        self.atn_nav_right.setIcon(QtGui.QIcon(":/icons/arrow487.png"))
        self.atn_nav_right.setToolTip('Load the next item in stack.')

        self.atn_nav_left = QtGui.QAction("&Previous Item", self)
        self.atn_nav_left.setIcon(QtGui.QIcon(":/icons/arrowhead7.png"))
        self.atn_nav_left.setToolTip('Load the previous item in stack.')

        self.wgt_stack_items = QtGui.QComboBox()

        spacer = QtGui.QWidget()
        spacer.setSizePolicy(QtGui.QSizePolicy.Expanding,
                             QtGui.QSizePolicy.Expanding)

        self.atn_open_sv = QtGui.QAction("&Next Item", self)
        self.atn_open_sv.setIcon(QtGui.QIcon(":/icons/document79.png"))
        self.atn_open_sv.setToolTip('Open in SpecView')

        self.atn_open_im = QtGui.QAction("&Next Item", self)
        self.atn_open_im.setIcon(QtGui.QIcon(":/icons/document79.png"))
        self.atn_open_im.setToolTip('Open in Image Viewer')

        self.addAction(self.atn_open_sv)
        self.addAction(self.atn_open_im)
        self.addWidget(spacer)
        self.addSeparator()
        self.addAction(self.atn_nav_left)
        self.addWidget(self.wgt_stack_items)
        self.addAction(self.atn_nav_right)

        self.atn_nav_left.setEnabled(False)
        self.atn_nav_right.setEnabled(False)

    def enable_all(self, enable):
        self.atn_nav_left.setEnabled(enable)
        self.atn_nav_right.setEnabled(enable)



