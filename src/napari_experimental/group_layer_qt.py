from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, Generator

from napari._qt.containers import QtNodeTreeModel, QtNodeTreeView
from qtpy.QtCore import QModelIndex, Qt

from napari_experimental.group_layer import GroupLayer

if TYPE_CHECKING:
    from qtpy.QtCore import QModelIndex
    from qtpy.QtWidgets import QWidget


class QtGroupLayerModel(QtNodeTreeModel[GroupLayer]):

    @property
    def root_index(self) -> QModelIndex:
        return self.nestedIndex(())

    @property
    def flatindex_to_index(self) -> Dict[int, QModelIndex]:
        """
        Return a dictionary that maps between flattened indices and the
        QModelIndex-es used internally by the model.

        Key: Value pairs are flattened index (int): model index (QModelIndex).
        """
        return {self.flattenedIndex(index): index for index in self}

    def __init__(self, root: GroupLayer, parent: QWidget = None):
        super().__init__(root, parent)
        self.setRoot(root)

    def __iter__(self):
        yield from self.traverse(self.root_index)

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

    def nChildren(self, index: QModelIndex) -> int:
        """
        The number of children (and grandchildren, etc) that this item in
        the model has.

        :param index: Model index of the item in question.
        """
        if index.model() is not self:
            raise IndexError("QModelIndex supplied is not for this model.")

        n_children = self.rowCount(index)
        for child_row in range(n_children):
            n_children += self.nChildren(index.child(child_row, 0))

        return n_children

    def flattenedIndex(self, index: QModelIndex) -> int:
        """
        Returns a flat index for the model item at the given QModelIndex.
        TODO: Skip groups?

        Flat indices are allocated to items from 0 ascending, starting from
        the root item and proceeding down the tree, recursing into branches
        before continuing.
        The diagram below provides an example tree and the corresponding
        flattened index:

        Root                Flat Index
        - Node1             0
        - Group1            1
          - Node11          2
          - Node12          3
          - Group11         4
            - Node111       5
          - Group12         6
            - Node121       7
        - Node2             8
        - Group2            9
          - Node21          10

        :param index: Model index to fetch flattened index of.
        """
        if index.model() is None:
            # Reached the top of the tree
            return -1
        elif index.model() is not self:
            raise IndexError("QModelIndex supplied is not for this model.")

        flat_index = index.row() + 1
        parent = index.parent()

        for child_number in range(index.row()):
            # Index must be bumped by the number of children this child has,
            # before returning.
            flat_index += self.nChildren(self.index(child_number, 0, parent))

        return flat_index + self.flattenedIndex(parent)

    def traverse(
        self, index: QModelIndex
    ) -> Generator[QModelIndex, None, None]:
        """
        Iterates over the QModelIndex-es of the items in the model,
        starting from the index provided and recursing through that
        item's branch.

        If index points to a Node, only that Node's index is yielded.
        If index points to a Group, the group's index, followed by the
        index-es of its children (and children's children, etc) are yielded.

        :param index: Model index to begin recursion from.
        """
        if index.isValid():
            yield index

        if self.hasChildren(index):
            for child in range(self.rowCount(index)):
                yield from self.traverse(self.index(child, 0, index))


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

    def model(self) -> QtGroupLayerModel:
        return super().model()
