from __future__ import annotations

from typing import TYPE_CHECKING, Iterable

from napari._qt.containers import QtNodeTreeModel, QtNodeTreeView
from napari.layers import Layer
from napari.utils.tree import Group

if TYPE_CHECKING:
    from qtpy.QtWidgets import QWidget


class GroupLayer(Group[Layer]):
    def __init__(
        self, children: Iterable[Layer] = (), name: str = "grouped layers"
    ) -> None:
        Group.__init__(self, children=children, name=name, basetype=Layer)


class QtLayerTreeModel(QtNodeTreeModel[Layer]):
    def __init__(self, root: GroupLayer, parent: QWidget = None):
        super().__init__(root, parent)
        self.setRoot(root)


class QtLayerTreeView(QtNodeTreeView):
    _root: GroupLayer
    model_class = QtLayerTreeModel

    def __init__(self, root: GroupLayer, parent: QWidget = None):
        super().__init__(root, parent)
