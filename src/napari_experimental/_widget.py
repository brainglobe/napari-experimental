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
    """
    Main plugin widget for interacting with GroupLayers.

    Parameters
    ----------
    viewer : napari.viewer.Viewer
        Main viewer instance containing (in particular) the LayerList.
    """

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

        # Consistency when adding / removing layers from main viewer,
        # changes are reflected in the GroupLayer view too
        self.global_layers.events.inserted.connect(
            self._new_layer_in_main_viewer
        )
        self.global_layers.events.removed.connect(
            self._removed_layer_in_main_viewer
        )
        self.group_layers.events.removed.connect(
            self._removed_layer_in_group_layers
        )
        # Impose layer order whenever layers get moved
        self.group_layers.events.moved.connect(self._on_layer_moved)

        self.add_group_button = QPushButton("Add empty layer group")
        self.add_group_button.clicked.connect(self._new_layer_group)

        self.enter_debugger = QPushButton("ENTER DEBUGGER")
        self.enter_debugger.clicked.connect(self._enter_debug)

        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.group_layers_controls)
        self.layout().addWidget(self.enter_debugger)
        self.layout().addWidget(self.add_group_button)
        self.layout().addWidget(self.group_layers_view)

    def _new_layer_group(self) -> None:
        """
        Action taken when creating a new, empty layer group
        in the widget.
        """
        # Still causes bugs when moving groups
        # inside other groups, to investigate!
        self.group_layers.add_new_group()

    # BEGIN FUNCTIONS TO ENSURE CONSISTENCY BETWEEN
    # MAIN VIEWER AND GROUP LAYERS VIEWER.
    # Functions in this block are un-necessary if the
    # group layers widget later replaces the main layer viewer.

    def _new_layer_in_main_viewer(self, event: Event) -> None:
        """
        When a new layer is added via the global_layers controls,
        the GroupLayers instance needs to update to include it.

        The new layer is inserted into the appropriate position in
        the Tree.

        Parameters
        ----------
        event : Event
            With attributes
            - index (in the LayerList the Layer was inserted),
            - value (layer that was inserted).
        """
        # New layers in the main viewer can come in either at the top,
        # or next to another layer (from duplications, etc).
        # As such, we need to take the index that the layer was inserted
        # at in the LayerList, and insert the new layer into our GroupLayer
        # structure in the correct position.
        old_order = self.group_layers.flat_index_order()
        # Due to LayerList and Tree structures having reversed indices
        insert_at_flat_index = len(old_order) - event.index
        # Potentially could have been added to the end of the tree, in which
        # case a new index would have to be created at the end of the tree
        # and there would be no nested index to lookup
        insert_at_nested_index = (
            old_order[insert_at_flat_index]
            if insert_at_flat_index < len(old_order)
            else len(self.group_layers)
        )
        self.group_layers.add_new_layer(
            layer_ptr=event.value, location=insert_at_nested_index
        )

    def _on_layer_moved(self, event: Event) -> None:
        """
        Actions to take after GroupLayers are reordered:
        - Impose layer order on the main viewer after an update.

        Parameters
        ----------
        event : Event
            Unused, but contains the old and new indices of the moved item.
        """
        new_order = self.group_layers.flat_index_order()
        # Since the LayerList viewer indexes in the reverse to our Tree model,
        # we must reverse the order provided.
        new_order.reverse()

        for new_position, layer in enumerate(
            [
                self.group_layers[nested_index].layer
                for nested_index in new_order
            ]
        ):
            currently_at = self.global_layers.index(layer)
            self.global_layers.move(currently_at, dest_index=new_position)

    def _removed_layer_in_main_viewer(self, event: Event) -> None:
        """
        Action taken when a layer is removed using the main LayerList
        viewer.

        Parameters
        ----------
        event : Event
            Emitted event with attributes
            - index (of removed layer in LayerList),
            - value (the layer that was removed).
        """
        self.group_layers.remove_layer_item(layer_ptr=event.value)

    def _removed_layer_in_group_layers(self, event: Event) -> None:
        """
        Action taken when a layer is removed using the GroupLayers view.

        Parameters
        ----------
        event : Event
            Emitted event with attributes
            - index (of the layer that was removed),
            - value (the layer that was removed).
        """
        layer_to_remove = event.value.layer
        if layer_to_remove in self.global_layers:
            self.global_layers.remove(layer_to_remove)

    # END FUNCTION BLOCK

    def _enter_debug(self) -> None:
        """
        Placeholder method that allows the developer to
        enter a DEBUG context with the widget as self.
        """
        pass
