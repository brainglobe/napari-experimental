from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

from napari._qt.containers import QtNodeTreeModel, QtNodeTreeView
from napari._qt.containers.qt_layer_model import ThumbnailRole
from napari._qt.qt_resources import get_current_stylesheet
from qtpy.QtCore import QModelIndex, QSize, Qt
from qtpy.QtGui import QDropEvent, QImage

from napari_experimental.group_layer import GroupLayer
from napari_experimental.group_layer_delegate import GroupLayerDelegate

if TYPE_CHECKING:
    from qtpy.QtWidgets import QWidget


class QtGroupLayerModel(QtNodeTreeModel[GroupLayer]):
    """
    A QTreeModel that works with the GroupLayer tree structure.
    See `napari._qt.containers.QtNodeTreeModel` for more information.

    Parameters
    ----------
    root : GroupLayer
        The root object from which to form the model.
    parent : QWidget, optional
        Parent QObject for the instance.
    """

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
                return (
                    Qt.CheckState.Checked
                    if item.visible
                    else Qt.CheckState.Unchecked
                )

        return super().data(index, role)

    def setData(
        self,
        index: QModelIndex,
        value: Any,
        role: int = Qt.ItemDataRole.EditRole,
    ) -> bool:
        item = self.getItem(index)
        if role == Qt.ItemDataRole.EditRole:
            item.name = value
            role = Qt.ItemDataRole.DisplayRole
        elif role == Qt.ItemDataRole.CheckStateRole:
            if not item.is_group():
                item.layer.visible = (
                    Qt.CheckState(value) == Qt.CheckState.Checked
                )
            else:
                item.visible = Qt.CheckState(value) == Qt.CheckState.Checked

                # Changing the visibility of a group will affect all its
                # children - emit data changed for them too
                for child_item in item.traverse():
                    child_index = self.nestedIndex(
                        child_item.index_from_root()
                    )
                    self.dataChanged.emit(child_index, child_index, [role])

        else:
            return super().setData(index, value, role=role)

        self.dataChanged.emit(index, index, [role])
        return True


class QtGroupLayerView(QtNodeTreeView):
    """
    A QTreeView that works with the QtGroupLayerModel model.
    See `napari._qt.containers.QtNodeTreeView` for more information.

    Parameters
    ----------
    root : GroupLayer
        The root object from which to form the model.
    parent : QWidget, optional
        Parent QObject for the instance.
    """

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

    def dropEvent(self, event: QDropEvent):
        # On drag and drop, selectionChanged isn't fired as the same items
        # remain selected in the view, and just their indexes/position is
        # changed. Here we force the view selection to be synced to the model
        # after drag and drop.
        super().dropEvent(event)
        self.sync_selection_from_view_to_model()

    def sync_selection_from_view_to_model(self):
        """Force model / group layer to select the same items as the view"""
        selected = [self.model().getItem(qi) for qi in self.selectedIndexes()]
        self._root.propagate_selection(event=None, new_selection=selected)
