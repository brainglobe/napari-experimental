"""
"""

from typing import TYPE_CHECKING, Tuple

from napari.components import LayerList
from napari.layers import Layer
from napari.utils.events import Event
from qtpy.QtCore import QModelIndex
from qtpy.QtWidgets import QPushButton, QVBoxLayout, QWidget

from napari_experimental.group_layer import GroupLayer, NodeWrappingLayer
from napari_experimental.group_layer_qt import (
    QtGroupLayerModel,
    QtGroupLayerView,
)

if TYPE_CHECKING:
    import napari


class GroupLayerWidget(QWidget):

    @property
    def global_layers(self) -> LayerList:
        return self.viewer.layers

    def __init__(self, viewer: "napari.viewer.Viewer"):
        super().__init__()

        self.viewer = viewer

        self.group_layers = GroupLayer(self.global_layers)
        self.group_layers_model = QtGroupLayerModel(
            self.group_layers, parent=self
        )
        self.group_layers_view = QtGroupLayerView(
            self.group_layers, parent=self
        )

        self.global_layers.events.inserted.connect(self._new_layer)
        self.global_layers.events.removed.connect(self._removed_layer)

        self.group_layers_view.clicked.connect(self._item_selected_in_view)

        self.add_group_button = QPushButton("Add empty layer group")
        self.add_group_button.clicked.connect(self._new_layer_group)

        self.enter_debugger = QPushButton("ENTER DEBUGGER")
        self.enter_debugger.clicked.connect(self._enter_debug)

        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.enter_debugger)
        self.layout().addWidget(self.add_group_button)
        self.layout().addWidget(self.group_layers_view)

    def _item_selected_in_view(self, selected_index: QModelIndex) -> None:
        """
        When the user clicks an item in the tree, this function runs
        """
        the_node = self.group_layers_model.getItem(selected_index)
        if isinstance(the_node, GroupLayer):
            pass
        elif isinstance(the_node, NodeWrappingLayer):
            the_layer: Layer = the_node.layer
            self.global_layers.selection.select_only(the_layer)
        pass

    def _new_layer_group(self) -> None:
        """ """
        # Still causes bugs when moving groups
        # inside other groups, to investigate!
        self.group_layers.add_new_item()

    def _new_layer(self, event: Event) -> None:
        """
        :param event: index, value (layer that was inserted)
        """
        self.group_layers.add_new_item(layer_ptr=event.value)

    def _removed_layer(self, event: Tuple[int, Layer]) -> None:
        """
        :param event: index, value (layer that was removed)
        """
        self.group_layers.remove_layer_item(layer_ptr=event.value)

    def _enter_debug(self) -> None:
        """Placeholder method that allows the developer to
        enter a DEBUG context with the widget as self."""
        pass
