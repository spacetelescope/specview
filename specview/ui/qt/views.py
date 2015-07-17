from specview.external.qt import QtGui, QtCore

from specview.ui.models import LayerDataTreeItem, SpectrumDataTreeItem
from specview.ui.qt.menus import SpectrumDataContextMenu


class BaseDataTree(QtGui.QTreeView):
    sig_current_changed = QtCore.Signal(QtCore.QModelIndex)
    sig_selected_changed = QtCore.Signal(list)

    def __init__(self, parent=None):
        super(BaseDataTree, self).__init__(parent)
        self._current_item = None
        self._selected_items = None

    def contextMenuEvent(self, menu_event):
        super(BaseDataTree, self).contextMenuEvent(menu_event)

        index = self.indexAt(menu_event.pos())
        model = index.model()

        if model is None:
            return

        item = model.itemFromIndex(index)
        parent_index = model.indexFromItem(item.parent)

        if isinstance(item, QtGui.QStandardItem):
            context_menu = SpectrumDataContextMenu(self)
            context_menu.atn_remove.triggered.connect(
                lambda: model.remove_data_item(index, parent_index))
            context_menu.exec_(menu_event.globalPos())

    def currentChanged(self, selected, deselected):
        super(BaseDataTree, self).currentChanged(selected, deselected)
        model = selected.model()

        if model is not None:
            self._current_item = model.itemFromIndex(selected)

            try:
                self.sig_current_changed.emit(model.mapToSource(selected))
            except AttributeError:
                self.sig_current_changed.emit(selected)
        else:
            self._current_item = None

    def selectionChanged(self, selected, deselected):
        super(BaseDataTree, self).selectionChanged(selected, deselected)
        self._selected_items = []

        for index in self.selectedIndexes():
            self._selected_items.append(index.model().itemFromIndex(index))

        self.sig_selected_changed.emit(self._selected_items)


class SpectrumDataTree(BaseDataTree):
    """
    Subclass TreeView so that we can implement events that'll give
    information about interacting with the view.
    """
    def __init__(self):
        super(SpectrumDataTree, self).__init__()
        self.setDragEnabled(True)
        self.header().hide()

    def setModel(self, model):
        super(SpectrumDataTree, self).setModel(model)
        model.sourceModel().sig_added_item.connect(self.set_selected_item)

    @property
    def current_item(self):
        return self._current_item

    @property
    def selected_items(self):
        return self._selected_items

    @QtCore.Slot(QtCore.QModelIndex)
    def set_selected_item(self, index):
        item = self.model().itemFromIndex(index)

        if isinstance(item, SpectrumDataTreeItem):
            self.setCurrentIndex(index)
            self._current_item = item
        else:
            self._current_item = None


class LayerDataTree(BaseDataTree):
    """
    Subclass TreeView so that we can implement events that'll give
    information about interacting with the view.
    """
    def __init__(self):
        super(LayerDataTree, self).__init__()
        self.setDragEnabled(True)
        self.header().hide()
        self.active_data_item = None
        self.showColumn(0)
        self.showColumn(1)

    def setModel(self, model):
        super(LayerDataTree, self).setModel(model)
        try:
            model.sourceModel().sig_added_item.connect(self.set_selected_item)
        except AttributeError:
            model.sig_added_item.connect(self.set_selected_item)

    @property
    def current_item(self):
        return self._current_item

    @property
    def selected_items(self):
        return self._selected_items

    @QtCore.Slot(QtCore.QModelIndex)
    def set_selected_item(self, index):
        item = self.model().itemFromIndex(index)

        if isinstance(item, LayerDataTreeItem):
            self.setCurrentIndex(index)
            self._current_item = item

    @QtCore.Slot(QtCore.QModelIndex)
    def set_root_index(self, selected):
        item = self.model().itemFromIndex(selected)
        self.set_root_item(item, selected)

    def set_root_item(self, item, selected=None):
        if selected is None:
            selected = self.model().indexFromItem(item)

        try:
            self.setRootIndex(self.model().mapFromSource(selected))
        except AttributeError:
            self.setRootIndex(selected)


class ModelTree(BaseDataTree):
    def __init__(self):
        super(ModelTree, self).__init__()
        self.header().hide()
        self._current_item = None

    def set_root_index(self, selected):
        item = self.model().itemFromIndex(selected)
        self.set_root_item(item, selected)

    def set_root_item(self, item, index=None):
        if index is None:
            index = self.model().indexFromItem(item)

        if isinstance(item, LayerDataTreeItem):
            print("SHOWING")
            self.showColumn(0)
            self.showColumn(1)
            # self.setEnabled(True)
            # self.parentWidget().setEnabled(True)
            self.setRootIndex(index)
            self.setColumnWidth(0, 150)
            self.setColumnWidth(1, 100)
            self._current_item = item
        else:
            print("HIDING")
            self.hideColumn(0)
            self.hideColumn(1)
            # self.setEnabled(False)
            # self.parentWidget().setEnabled(False)
            self._current_item = None

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
