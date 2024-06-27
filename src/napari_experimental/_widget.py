"""
"""

from typing import TYPE_CHECKING

from napari.components import LayerList
from napari.utils.events import Event
from qtpy.QtWidgets import QPushButton, QVBoxLayout, QWidget

from napari_experimental.group_layer import GroupLayer
from napari_experimental.group_layer_controls import (
    QtGroupLayerControlsContainer,
)
from napari_experimental.group_layer_qt import (
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

        self.group_layers = GroupLayer(*self.global_layers.__reversed__())
        self.group_layers_view = QtGroupLayerView(
            self.group_layers, parent=self
        )
        self.group_layers_controls = QtGroupLayerControlsContainer(
            self.viewer, self.group_layers
        )

        self.global_layers.events.inserted.connect(self._new_layer)
        self.global_layers.events.removed.connect(self._removed_layer)
        self.global_layers.events.moved.connect(self._on_layer_move)

        # Impose any layer reorderings on the global layers viewer.
        # NOTE: May be slow since this will happen whenever rows move,
        # and we will reconstruct the whole layer order each time even
        # if only one row moves, for example.
        self.group_layers_view.model().rowsMoved.connect(
            self._impose_layer_order
        )

        self.add_group_button = QPushButton("Add empty layer group")
        self.add_group_button.clicked.connect(self._new_layer_group)

        self.enter_debugger = QPushButton("ENTER DEBUGGER")
        self.enter_debugger.clicked.connect(self._enter_debug)

        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.group_layers_controls)
        self.layout().addWidget(self.enter_debugger)
        self.layout().addWidget(self.add_group_button)
        self.layout().addWidget(self.group_layers_view)

    def _impose_layer_order(self) -> None:
        """
        When the user clicks the impose order button, update the order that
        the Layers appear in the main viewer.
        """
        _the_model = self.group_layers_view.model()
        current_flat_order = _the_model.flatindex_to_index

        layer_priority = {
            _the_model.getItem(q_index).layer: flat_index
            for flat_index, q_index in current_flat_order.items()
            if _the_model.getItem(q_index).is_tracking
        }
        # Ensure that we order layers and indices correctly
        # NOTE the - sign here: trees index from top down, but layer order
        # is from bottom up!
        layer_order = sorted(
            layer_priority.keys(), key=lambda layer: -layer_priority[layer]
        )

        # Reorder the global layers based on this order
        current_insertion_index = 0
        for layer in layer_order:
            currently_at = self.global_layers.index(layer)
            self.global_layers.move(
                currently_at, dest_index=current_insertion_index
            )
            current_insertion_index += 1
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
        # TODO: insert_at argument needs to sync.
        # Note both
        # (a) the reverse index difficulty, and
        # (b) the un-flattening ambiguity
        # Might be able to re-use some functionality from _on_layer_move...
        # Will need to be able to:
        # - Convert the layerlist index to the correct (multi-index) of the
        # tree, accounting for the fact that groups are counted by the index
        # in our structure, but aren't in LayerList...
        # - Determine the correct place to insert in the event that we're
        # inserting before a group item...
        self.group_layers.add_new_item(insert_at=0, layer_ptr=event.value)
        raise NotImplementedError()

    def _on_layer_move(self, event: Event) -> None:
        """
        :param event: index (moved from), new_index (moved to), value
        """
        raise NotImplementedError()

    def _removed_layer(self, event: Event) -> None:
        """
        :param event: index, value (layer that was removed)
        """
        self.group_layers.remove_layer_item(layer_ptr=event.value)

    def _enter_debug(self) -> None:
        """Placeholder method that allows the developer to
        enter a DEBUG context with the widget as self."""
        pass
