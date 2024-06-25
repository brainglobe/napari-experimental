from __future__ import annotations

from typing import TYPE_CHECKING, Any

from napari._qt.containers import QtNodeTreeModel, QtNodeTreeView
from qtpy.QtCore import QModelIndex, Qt

from napari_experimental.group_layer import GroupLayer

if TYPE_CHECKING:
    from qtpy.QtWidgets import QWidget


class QtGroupLayerModel(QtNodeTreeModel[GroupLayer]):

    def __init__(self, root: GroupLayer, parent: QWidget = None):
        super().__init__(root, parent)
        self.setRoot(root)

    def data(self, index: QModelIndex, role: Qt.ItemDataRole):
        """Return data stored under ``role`` for the item at ``index``.

        A given class:`QModelIndex` can store multiple types of data, each with
        its own "ItemDataRole".
        """
        item = self.getItem(index)
        if role == Qt.ItemDataRole.DisplayRole:
            return item._node_name()
        elif role == Qt.ItemDataRole.EditRole:
            # used to populate line edit when editing
            return item._node_name()
        elif role == Qt.ItemDataRole.UserRole:
            return self.getItem(index)
        return None

    def setData(
        self,
        index: QModelIndex,
        value: Any,
        role: int = Qt.ItemDataRole.EditRole,
    ) -> bool:
        if role == Qt.ItemDataRole.EditRole:
            self.getItem(index).name = value
            self.dataChanged.emit(index, index, [role])
            return True
        else:
            return False


class QtGroupLayerView(QtNodeTreeView):
    _root: GroupLayer
    model_class = QtGroupLayerModel

    def __init__(self, root: GroupLayer, parent: QWidget = None):
        super().__init__(root, parent)
        self.setRoot(root)

    def setRoot(self, root: GroupLayer):
        """Override setRoot to ensure .model is a QtGroupLayerModel"""
        self._root = root
        self.setModel(QtGroupLayerModel(root, self))

        # from _BaseEventedItemView
        root.selection.events.changed.connect(self._on_py_selection_change)
        root.selection.events._current.connect(self._on_py_current_change)
        self._sync_selection_models()

        # from QtNodeTreeView
        self.model().rowsRemoved.connect(self._redecorate_root)
        self.model().rowsInserted.connect(self._redecorate_root)
        self._redecorate_root()
