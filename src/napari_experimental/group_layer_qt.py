from __future__ import annotations

from itertools import chain, repeat
from pathlib import Path
from typing import TYPE_CHECKING, Any

from napari._qt.containers import QtNodeTreeModel, QtNodeTreeView
from napari._qt.containers._base_item_view import index_of
from napari._qt.qt_resources import get_current_stylesheet
from napari.utils.events import Event
from qtpy.QtCore import QModelIndex, QSize, Qt
from qtpy.QtGui import QImage

from napari_experimental.group_layer import GroupLayer
from napari_experimental.group_layer_delegate import GroupLayerDelegate

if TYPE_CHECKING:
    from qtpy.QtWidgets import QWidget


ThumbnailRole = Qt.UserRole + 2


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
        # Match size setting in QtLayerListModel data()
        elif role == Qt.ItemDataRole.SizeHintRole:
            return QSize(200, 34)
        # Match thumbnail retrieval in QtLayerListModel data()
        elif role == ThumbnailRole and not item.is_group():
            thumbnail = item.layer.thumbnail
            return QImage(
                thumbnail,
                thumbnail.shape[1],
                thumbnail.shape[0],
                QImage.Format_RGBA8888,
            )
        # Match alignment of text in QtLayerListModel data()
        elif role == Qt.ItemDataRole.TextAlignmentRole:
            return Qt.AlignCenter
        # Match check state in QtLayerListModel data()
        elif role == Qt.ItemDataRole.CheckStateRole:
            if not item.is_group():
                return (
                    Qt.CheckState.Checked
                    if item.layer.visible
                    else Qt.CheckState.Unchecked
                )
            else:
                return Qt.CheckState.Checked
        return None

    def setData(
        self,
        index: QModelIndex,
        value: Any,
        role: int = Qt.ItemDataRole.EditRole,
    ) -> bool:
        item = self.getItem(index)
        if role == Qt.ItemDataRole.EditRole:
            item.name = value
            self.dataChanged.emit(index, index, [role])
            return True
        elif role == Qt.ItemDataRole.CheckStateRole:
            if not item.is_group():
                item.layer.visible = (
                    Qt.CheckState(value) == Qt.CheckState.Checked
                )
            return True
        else:
            return False


class QtGroupLayerView(QtNodeTreeView):
    _root: GroupLayer
    model_class = QtGroupLayerModel

    def __init__(self, root: GroupLayer, parent: QWidget = None):
        super().__init__(root, parent)
        self.setRoot(root)

        grouplayer_delegate = GroupLayerDelegate()
        self.setItemDelegate(grouplayer_delegate)

        # Keep existing style and add additional items from 'tree.qss'
        # Tree.qss matches styles for QtListView and QtLayerList from
        # 02_custom.qss in Napari
        stylesheet = get_current_stylesheet(
            extra=[str(Path(__file__).parent / "styles" / "tree.qss")]
        )
        self.setStyleSheet(stylesheet)

    def _on_py_selection_change(self, event: Event):
        """Same as parent in _base_item_view, but clears selection if it tries
        to modify an invalid one"""
        sm = self.selectionModel()
        for is_selected, idx in chain(
            zip(repeat(sm.SelectionFlag.Select), event.added),
            zip(repeat(sm.SelectionFlag.Deselect), event.removed),
        ):
            model_idx = index_of(self.model(), idx)
            if model_idx.isValid():
                sm.select(model_idx, is_selected)
            else:
                sm.clearSelection()
        pass

    def _connect_events_for_new_item(self, event: Event):
        self._connect_events(event.value)

    def _connect_events(self, group_layer):
        if group_layer.is_group():
            # Make sure that when new nodes are added, we also react to
            # changes in their selection
            group_layer.events.inserted.connect(
                self._connect_events_for_new_item
            )
            # group_layer.events.removed.disconnect(self._remove)
            group_layer.selection.events.changed.connect(
                self._on_py_selection_change
            )
            group_layer.selection.events._current.connect(
                self._on_py_current_change
            )

            for node in group_layer:
                self._connect_events(node)

    def setRoot(self, root: GroupLayer):
        """Override setRoot to ensure .model is a QtGroupLayerModel"""
        self._root = root
        self.setModel(QtGroupLayerModel(root, self))

        # from _BaseEventedItemView
        # Needs to react to changes at all levels in the tree
        # self._connect_events(root)
        root.selection.events.changed.connect(self._on_py_selection_change)
        root.selection.events._current.connect(self._on_py_current_change)
        self._sync_selection_models()

        # from QtNodeTreeView
        self.model().rowsRemoved.connect(self._redecorate_root)
        self.model().rowsInserted.connect(self._redecorate_root)
        self._redecorate_root()
