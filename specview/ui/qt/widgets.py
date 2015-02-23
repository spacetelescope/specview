from PyQt4 import QtGui, QtCore, Qt
from pyqtgraph.console import ConsoleWidget
from specview.ui.qt.custom import ModelViewItem


class SpecViewTree(QtGui.QTreeView):
    """
    Subclass TreeView so that we can implement events that'll give
    information about interacting with the view.
    """
    def __init__(self):
        super(SpecViewTree, self).__init__()
        self.setDragEnabled(True)

    # def selectionChanged(self, selected, deselected):
    #     index = self.selectedIndexes()[0]
    #     self.current_item = index.model().itemFromIndex(index).item

    @property
    def current_item(self):
        index = self.currentIndex()
        return index.model().itemFromIndex(index)

    @property
    def selected_items(self):
        selected_list = []

        for index in self.selectedIndexes():
            selected_list.append(index.model().itemFromIndex(index).item)

        return selected_list

    def add_model(self, model):
        pass


class ModelEditorTree(QtGui.QTreeView):
    def __init__(self):
        super(ModelEditorTree, self).__init__()
        self.setDragEnabled(True)

    # def selectionChanged(self, selected, deselected):
    #     index = self.selectedIndexes()[0]
    #     self.current_item = index.model().itemFromIndex(index).item

    @property
    def current_item(self):
        index = self.currentIndex()
        return index.model().itemFromIndex(index)

    @property
    def selected_items(self):
        selected_list = []

        for index in self.selectedIndexes():
            selected_list.append(index.model().itemFromIndex(index).item)

        return selected_list

    def set_parent_item(self, parent):
        print("Setting items")


class BaseDockWidget(QtGui.QDockWidget):
    """
    Subclass of dock widget.
    """
    def __init__(self):
        super(BaseDockWidget, self).__init__()

        # Set empty main widget with layout
        main_widget = QtGui.QWidget()
        self.vb_layout = QtGui.QVBoxLayout()
        main_widget.setLayout(self.vb_layout)

        # Set main window
        self.setWidget(main_widget)

    def add_widget(self, widget):
        self.vb_layout.addWidget(widget)

    def add_layout(self, layout):
        self.vb_layout.addLayout(layout)


class DataDockWidget(BaseDockWidget):
    def __init__(self):
        super(DataDockWidget, self).__init__()
        self.setWindowTitle("Data")

        # Set allowed areas and behavior
        self.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea |
                             QtCore.Qt.RightDockWidgetArea)

        # Add TreeView widget
        self.wgt_data_tree = SpecViewTree()
        self.wgt_data_tree.setSelectionMode(
            QtGui.QAbstractItemView.ExtendedSelection)

        # Set Plotting buttons
        self.btn_create_plot = QtGui.QToolButton()
        self.btn_add_plot = QtGui.QToolButton()

        # Arithmetic buttons
        # self.btn_sum = QtGui.QToolButton()
        # self.btn_diff = QtGui.QToolButton()
        # self.btn_mult = QtGui.QToolButton()
        # self.btn_div = QtGui.QToolButton()

        # Add to main layout
        self.add_widget(self.wgt_data_tree)

        # Setup buttons
        hb_layout = QtGui.QHBoxLayout()
        hb_layout.addWidget(self.btn_create_plot)
        hb_layout.addWidget(self.btn_add_plot)
        hb_layout.addStretch()

        self.add_layout(hb_layout)


class InfoDockWidget(BaseDockWidget):
    def __init__(self):
        super(InfoDockWidget, self).__init__()
        self.setWindowTitle("Info")

        self.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea |
                             QtCore.Qt.RightDockWidgetArea)

        self.wgt_text_edit = QtGui.QTextEdit()

        self.add_widget(self.wgt_text_edit)


class ConsoleDockWidget(BaseDockWidget):
    def __init__(self):
        super(ConsoleDockWidget, self).__init__()
        self.setWindowTitle("Console")

        self.setAllowedAreas(QtCore.Qt.BottomDockWidgetArea)

        self.wgt_console = ConsoleWidget()

        self.add_widget(self.wgt_console)

        self.setVisible(False)

class ModelDockWidget(BaseDockWidget):
    """
    TODO: make dedicated class for handling getting/retreiving selected model
    data, and to handle creating the ModelViewItem instance.
    """
    from specview.analysis import model_fitting

    def __init__(self):
        super(ModelDockWidget, self).__init__()

        self.setWindowTitle("Model Editor")

        self.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea |
                             QtCore.Qt.RightDockWidgetArea)

        # Add TreeView widget
        self.wgt_model_tree = ModelEditorTree()
        self.wgt_model_tree.setSelectionMode(
            QtGui.QAbstractItemView.ExtendedSelection)

        self.wgt_model_selector = QtGui.QComboBox()
        self.wgt_model_selector.addItems(self.model_fitting.all_models.keys())

        self.btn_add_model = QtGui.QToolButton()

        hb_layout = QtGui.QHBoxLayout()
        hb_layout.addWidget(self.wgt_model_selector)
        hb_layout.addWidget(self.btn_add_model)

        self.add_layout(hb_layout)
        self.add_widget(self.wgt_model_tree)

        self.wgt_fit_selector = QtGui.QComboBox()
        self.wgt_fit_selector.addItems(self.model_fitting.all_fitters.keys())

        self.btn_perform_fit = QtGui.QPushButton("&Fit")

        self.add_widget(self.wgt_fit_selector)
        self.add_widget(self.btn_perform_fit)

    def get_model(self):
        new_model = ModelViewItem(
            self.model_fitting.all_models[
                self.wgt_model_selector.currentText()
            ]
        )
        return new_model