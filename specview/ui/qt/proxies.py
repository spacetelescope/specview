from specview.external.qt import QtGui, QtCore
from specview.ui.items import SpectrumDataTreeItem, LayerDataTreeItem
from specview.ui.models import DataTreeModel


class BaseProxyModel(QtGui.QSortFilterProxyModel):

    def filterAcceptsRow(self, row_num, source_parent):
        # Check if the current row matches
        if self.filter_accepts_row_itself(row_num, source_parent):
            return True

        # Traverse up all the way to root and check if any of them match
        # if self.filter_accepts_any_parent(source_parent):
        #     return True

        # Finally, check if any of the children match
        return False

    def filter_accepts_any_parent(self, parent):
        while parent.isValid():
            if self.filter_accepts_row_itself(parent.row(), parent.parent()):
                return True
            parent = parent.parent()
        return False

    def has_accepted_children(self, row_num, parent):
        model = self.sourceModel()
        source_index = model.index(row_num, 0, parent)

        children_count =  model.rowCount(source_index)
        for i in xrange(children_count):
            if self.filterAcceptsRow(i, source_index):
                return True
        return False

    def indexFromItem(self, item):
        return self.sourceModel().indexFromItem(item)


class DataProxyModel(BaseProxyModel): #self.has_accepted_children(row_num, source_parent)

    def filter_accepts_row_itself(self, row_num, parent):
        source_index = self.sourceModel().index(row_num, 0, parent)
        item = self.sourceModel().itemFromIndex(source_index)

        if isinstance(item, SpectrumDataTreeItem):
            return True

        return False

    def itemFromIndex(self, index):
        if isinstance(index.model(), DataTreeModel):
            return self.sourceModel().itemFromIndex(index)
        elif isinstance(index.model(), DataProxyModel):
            index = self.mapToSource(index)
            return self.sourceModel().itemFromIndex(index)
        else:
            raise Exception("Unrecognized model {}".format(index.model()))

    def remove_data_item(self, index, parent_index):
        if isinstance(index.model(), DataTreeModel):
            return self.sourceModel().remove_data_item(index, parent_index)
        elif isinstance(index.model(), DataProxyModel):
            index = self.mapToSource(index)
            return self.sourceModel().remove_data_item(index, parent_index)
        else:
            raise Exception("Unrecognized model {}".format(index.model()))


class LayerProxyModel(BaseProxyModel):

    def filter_accepts_row_itself(self, row_num, source_parent):
        source_index = self.sourceModel().index(row_num, 0, source_parent)
        item = self.sourceModel().itemFromIndex(source_index)

        if isinstance(item, LayerDataTreeItem):
            return True

        if isinstance(item, SpectrumDataTreeItem) and item.hasChildren():
            return True

        return False

    def itemFromIndex(self, index):
        if isinstance(index.model(), DataTreeModel):
            return self.sourceModel().itemFromIndex(index)
        elif isinstance(index.model(), LayerProxyModel):
            index = self.mapToSource(index)
            return self.sourceModel().itemFromIndex(index)
        elif index is None:
            return None
        else:
            raise Warning("Unrecognized model {}".format(index.model()))

    def remove_data_item(self, index, parent_index):
        if isinstance(index.model(), DataTreeModel):
            return self.sourceModel().remove_data_item(index, parent_index)
        elif isinstance(index.model(), LayerProxyModel):
            index = self.mapToSource(index)
            return self.sourceModel().remove_data_item(index, parent_index)
        else:
            raise Exception("Unrecognized model {}".format(index.model()))
