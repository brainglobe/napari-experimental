"""
"""

from typing import TYPE_CHECKING, Tuple

from napari.components import LayerList
from napari.layers import Layer
from napari.utils.events import Event
from qtpy.QtWidgets import QPushButton, QVBoxLayout, QWidget

from napari_experimental.names_only import (
    LayerNamesTracker,
    QtLayerNamesTreeModel,
    QtLayerNamesTreeView,
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

        self.layer_names = LayerNamesTracker(self.global_layers)
        self.layer_names_model = QtLayerNamesTreeModel(
            self.layer_names, parent=self
        )
        self.layer_names_view = QtLayerNamesTreeView(
            self.layer_names, parent=self
        )

        self.global_layers.events.inserted.connect(self._new_layer)
        self.global_layers.events.removed.connect(self._removed_layer)

        self.add_group_button = QPushButton("Add empty layer group")
        self.add_group_button.clicked.connect(self._new_layer_group)

        self.enter_debugger = QPushButton("ENTER DEBUGGER")
        self.enter_debugger.clicked.connect(self._enter_debug)

        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.enter_debugger)
        self.layout().addWidget(self.add_group_button)
        self.layout().addWidget(self.layer_names_view)

    def _new_layer_group(self) -> None:
        """ """
        # Still causes bugs when moving groups
        # inside other groups, to investigate!
        self.layer_names.add_new_item()

    def _new_layer(self, event: Event) -> None:
        """
        :param event: index, value (layer that was inserted)
        """
        self.layer_names.add_new_item(layer_ptr=event.value)

    def _removed_layer(self, event: Tuple[int, Layer]) -> None:
        """
        :param event: index, value (layer that was removed)
        """
        self.layer_names.remove_layer_item(layer_ptr=event.value)

    def _enter_debug(self) -> None:
        """Placeholder method that allows the developer to
        enter a DEBUG context with the widget as self."""
        pass
