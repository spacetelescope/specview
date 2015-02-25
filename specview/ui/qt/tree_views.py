from PyQt4 import QtGui, QtCore

from specview.ui.model import LayerDataTreeItem


class SpectrumDataTree(QtGui.QTreeView):
    """
    Subclass TreeView so that we can implement events that'll give
    information about interacting with the view.
    """
    sig_current_changed = QtCore.pyqtSignal(object)
    sig_selected_changed = QtCore.pyqtSignal(list)

    def __init__(self):
        super(SpectrumDataTree, self).__init__()
        self.setDragEnabled(True)
        self._current_item = None
        self._selected_items = None

    def currentChanged(self, selected, deselected):
        super(SpectrumDataTree, self).currentChanged(selected, deselected)
        self._current_item = selected.model().itemFromIndex(selected)
        self.sig_current_changed.emit(self.current_item)

    def selectionChanged(self, selected, deselected):
        super(SpectrumDataTree, self).selectionChanged(selected, deselected)
        self._selected_items = []

        for index in self.selectedIndexes():
            self._selected_items.append(index.model().itemFromIndex(index))

        self.sig_selected_changed.emit(self.selected_items)

    @property
    def current_item(self):
        print(self._current_item)
        return self._current_item

    @property
    def selected_items(self):
        return self._selected_items


class ModelTree(QtGui.QTreeView):
    def __init__(self):
        super(ModelTree, self).__init__()
        self.active_layer = None

    # def selectionChanged(self, selected, deselected):
    #     index = self.selectedIndexes()[0]
    #     self.current_item = index.model().itemFromIndex(index).item

    def set_root_index(self, layer, index):
        if isinstance(layer, LayerDataTreeItem):
            self.setEnabled(True)
            self.setRootIndex(index)
            self.active_layer = layer
        else:
            self.setEnabled(False)

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


