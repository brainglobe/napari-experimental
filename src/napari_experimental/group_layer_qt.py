from __future__ import annotations

from typing import TYPE_CHECKING

from napari._qt.containers import QtNodeTreeModel, QtNodeTreeView
from qtpy.QtCore import QModelIndex
from qtpy.QtWidgets import QStyledItemDelegate, QWidget

from napari_experimental.group_layer import GroupLayer, NodeWrappingLayer

if TYPE_CHECKING:
    from qtpy.QtWidgets import QWidget


class QtGroupLayerModel(QtNodeTreeModel[GroupLayer]):

    def __init__(self, root: GroupLayer, parent: QWidget = None):
        super().__init__(root, parent)
        self.setRoot(root)


class QtGroupLayerDelegate(QStyledItemDelegate):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def setModelData(
        self, editor: QWidget, model: QtGroupLayerModel, index: QModelIndex
    ) -> None:
        item_to_edit = model.getItem(index)
        if isinstance(item_to_edit, NodeWrappingLayer) and editor.text():
            item_to_edit.layer.name = editor.text()


class QtGroupLayerView(QtNodeTreeView):
    _root: GroupLayer
    model_class = QtGroupLayerModel

    def __init__(self, root: GroupLayer, parent: QWidget = None):
        super().__init__(root, parent)
        self.setRoot(root)

        self.setItemDelegate(QtGroupLayerDelegate())
