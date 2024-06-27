"""
"""

from typing import TYPE_CHECKING, Optional, Tuple

from napari._app_model import get_app
from napari.components import LayerList
from napari.layers import Layer
from napari.utils.events import Event
from qtpy.QtWidgets import QPushButton, QVBoxLayout, QWidget

from napari_experimental.group_layer import GroupLayer
from napari_experimental.group_layer_actions import GROUP_LAYER_ACTIONS
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
        get_app().register_actions(GROUP_LAYER_ACTIONS)
        get_app().injection_store.register(
            providers=[(self._provide_active_group_layer,)]
        )

        self.group_layers = GroupLayer(*self.global_layers)
        self.group_layers_view = QtGroupLayerView(
            self.group_layers, parent=self
        )
        self.group_layers_controls = QtGroupLayerControlsContainer(
            self.viewer, self.group_layers
        )

        self.global_layers.events.inserted.connect(self._new_layer)
        self.global_layers.events.removed.connect(self._removed_layer)

        self.add_group_button = QPushButton("Add empty layer group")
        self.add_group_button.clicked.connect(self._new_layer_group)

        self.enter_debugger = QPushButton("ENTER DEBUGGER")
        self.enter_debugger.clicked.connect(self._enter_debug)

        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.group_layers_controls)
        self.layout().addWidget(self.enter_debugger)
        self.layout().addWidget(self.add_group_button)
        self.layout().addWidget(self.group_layers_view)

    # Provider for active group_layer, in style of
    # _app_model/injection/_providers.py in napari
    def _provide_active_group_layer(self) -> Optional[GroupLayer]:
        return self.group_layers

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
