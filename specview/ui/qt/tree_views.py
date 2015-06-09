from ...external.qt import QtGui, QtCore

from specview.ui.model import LayerDataTreeItem
from specview.ui.qt.menus import SpectrumDataContextMenu
from specview.ui.qt.tree_items import ParameterDataTreeItem


class BaseDataTree(QtGui.QTreeView):
    # TODO: get rid of nasty try/excepts
    try:
        sig_current_changed = QtCore.pyqtSignal(QtCore.QModelIndex)
        sig_selected_changed = QtCore.pyqtSignal(list)
        sig_updated = QtCore.pyqtSignal(ParameterDataTreeItem)
    except AttributeError:
        sig_current_changed = QtCore.Signal(QtCore.QModelIndex)
        sig_selected_changed = QtCore.Signal(list)
        sig_updated = QtCore.Signal(ParameterDataTreeItem)

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
            self.sig_current_changed.emit(selected)
        else:
            self._current_item = None
            self.sig_current_changed.emit(QtCore.QModelIndex())

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
        model.sig_added_item.connect(self.set_selected_item)

    @property
    def current_item(self):
        return self._current_item

    @property
    def selected_items(self):
        return self._selected_items

    # --- slots
    def set_selected_item(self, index):
        item = index.model().itemFromIndex(index)

        if isinstance(item, LayerDataTreeItem):
            self.setCurrentIndex(index)
            self._current_item = item


class ModelTree(BaseDataTree):
    def __init__(self):
        super(ModelTree, self).__init__()
        self.active_layer = None
        self.header().hide()

        self.signal_updated = None

    # def selectionChanged(self, selected, deselected):
    #     index = self.selectedIndexes()[0]
    #     self.current_item = index.model().itemFromIndex(index).item

    def set_root_index(self, selected):
        model = selected.model()

        if model is None:
            return

        item = selected.model().itemFromIndex(selected)

        if isinstance(item, LayerDataTreeItem):

            self.signal_updated = item.signal_updated

            self.showColumn(0)
            self.showColumn(1)
            # self.setEnabled(True)
            self.parentWidget().setEnabled(True)
            self.setRootIndex(selected)
            self.setColumnWidth(0, 150)
            self.setColumnWidth(1, 100)
            self.active_layer = item
        else:
            self.active_layer = None
            self.hideColumn(0)
            self.hideColumn(1)
            # self.setEnabled(False)
            self.parentWidget().setEnabled(False)

    # def currentChanged(self, selected, deselected):
    #     model = selected.model()
    #
    #     if model is not None:
    #         self._current_item = model.itemFromIndex(selected)
    #         self.sig_updated.emit(self._current_item)
    #     else:
    #         self._current_item = None
    #         self.sig_updated.emit(None)

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


