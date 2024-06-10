"""
This module contains an experimental implementation of a layers widget.
"""
from typing import TYPE_CHECKING

from qtpy.QtWidgets import QVBoxLayout, QWidget
from qtpy.QtCore import QModelIndex

if TYPE_CHECKING:
    import napari


from napari._qt.containers import QtLayerList
from napari.components import LayerList

from napari_experimental.qt_layer_tree_model import QtLayerTreeModel, QtLayerTreeView
from napari.utils.events.containers import SelectableEventedList

from napari_experimental.layergroup import LayerGroup
from napari.utils.tree import Group, Node

class LayersWidget(QWidget):
    def __init__(self, viewer: "napari.viewer.Viewer"):
        super().__init__()

        self.viewer = viewer
        self.viewer.layers.events.inserted.connect(self._on_add_layer)
        self.viewer.layers.events.removed.connect(self._on_remove_layer)

        self.layer_list = LayerList()
        qt_layer_list = QtLayerList(root=self.layer_list, parent=self)

        dummy_layer_group = LayerGroup(name="dummy")
        [print(key) for key in dummy_layer_group.events._emitters.keys()]
        assert isinstance(dummy_layer_group, SelectableEventedList)
        self.layer_tree_model = QtLayerTreeModel(dummy_layer_group, parent=self)
        self.qt_layer_tree = QtLayerTreeView(parent=self)
        self.qt_layer_tree.setModel(self.layer_tree_model)
        
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.qt_layer_tree)
        self.layout().addWidget(qt_layer_list)

    def _on_add_layer(self, event):
        added_layer = event.value
        self.layer_list.append(added_layer)
        root = self.layer_tree_model.getItem(QModelIndex())
        assert root.is_group()
        node = Node(added_layer.name)
        root.insert(0, node)

    def _on_remove_layer(self, event):
        removed_layer = event.value
        self.layer_list.remove(removed_layer)
        root = self.layer_tree_model.getItem(QModelIndex())
        root.remove(removed_layer.name)
