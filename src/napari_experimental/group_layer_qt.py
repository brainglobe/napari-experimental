from __future__ import annotations

from typing import TYPE_CHECKING

from napari._qt.containers import QtNodeTreeModel, QtNodeTreeView

from napari_experimental.group_layer import GroupLayer

if TYPE_CHECKING:
    from qtpy.QtWidgets import QWidget


class QtGroupLayerModel(QtNodeTreeModel[GroupLayer]):

    def __init__(self, root: GroupLayer, parent: QWidget = None):
        super().__init__(root, parent)
        self.setRoot(root)


class QtGroupLayerView(QtNodeTreeView):
    _root: GroupLayer
    model_class = QtGroupLayerModel

    def __init__(self, root: GroupLayer, parent: QWidget = None):
        super().__init__(root, parent)
        self.setRoot(root)
