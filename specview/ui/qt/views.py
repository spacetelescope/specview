from PyQt4 import QtGui, QtCore, Qt
from pyqtgraph.console import ConsoleWidget
from models import LayerDataTreeItem


class SpectrumDataTree(QtGui.QTreeView):
    """
    Subclass TreeView so that we can implement events that'll give
    information about interacting with the view.
    """
    def __init__(self):
        super(SpectrumDataTree, self).__init__()
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
            selected_list.append(index.model().itemFromIndex(index))

        return selected_list


class ModelTree(QtGui.QTreeView):
    def __init__(self):
        super(ModelTree, self).__init__()
        self.setDragEnabled(True)

    # def selectionChanged(self, selected, deselected):
    #     index = self.selectedIndexes()[0]
    #     self.current_item = index.model().itemFromIndex(index).item

    def set_root_index(self, item, index):
        if isinstance(item, LayerDataTreeItem):
            self.setRootIndex(index)

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


