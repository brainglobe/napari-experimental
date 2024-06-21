from typing import TYPE_CHECKING

from napari._qt.layer_controls import QtLayerControlsContainer
from napari._qt.layer_controls.qt_layer_controls_container import (
    create_qt_layer_controls,
)
from napari.utils.events import Event
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QFrame, QHBoxLayout, QLabel

from napari_experimental.group_layer import GroupLayer
from napari_experimental.group_layer_node import GroupLayerNode

if TYPE_CHECKING:
    import napari


class QtGroupLayerControls(QFrame):
    """Group layer controls - for now, this just displays a message to the
    user"""

    def __init__(self) -> None:
        super().__init__()
        self.setLayout(QHBoxLayout())

        label = QLabel("Select individual layer to view layer controls")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon = QLabel()
        icon.setObjectName("info_icon")
        icon.setMaximumHeight(50)

        self.layout().addWidget(icon)
        self.layout().addWidget(label)


class QtGroupLayerControlsContainer(QtLayerControlsContainer):

    def __init__(
        self, viewer: "napari.viewer.Viewer", group_layers: GroupLayer
    ) -> None:
        super().__init__(viewer)

        # Disconnect controls from any layer events from the viewer -
        # we want to only use events from group_layers
        self.viewer.layers.events.inserted.disconnect(self._add)
        self.viewer.layers.events.removed.disconnect(self._remove)
        self.viewer.layers.selection.events.active.disconnect(self._display)

        # Initialise controls for any layers already present in group_layers
        self._initialise_controls(group_layers)
        self._display_item(group_layers.selection.active)

        # Sync with changes to group layers
        group_layers.events.inserted.connect(self._add)
        group_layers.events.removed.connect(self._remove)
        group_layers.selection.events.active.connect(self._display)

    def _initialise_controls(self, group_layers):
        """Initialise controls for any items already present in group
        layers"""
        for item in group_layers:
            if item.is_group():
                self._initialise_controls(item)

            self._add_item(item)

    def _add(self, event: Event):
        """Add the controls target item to the list of control widgets.

        Parameters
        ----------
        event : Event
            Event with the target item at `event.value`.
        """
        item = event.value
        self._add_item(item)

    def _add_item(self, item: GroupLayer | GroupLayerNode):
        if item.is_group():
            controls = QtGroupLayerControls()
        else:
            layer = item.layer
            controls = create_qt_layer_controls(layer)

        controls.ndisplay = self.viewer.dims.ndisplay
        self.addWidget(controls)
        self.widgets[item] = controls

    def _display(self, event: Event):
        """Change the displayed controls to be those of the target item.

        Parameters
        ----------
        event : Event
            Event with the target item at `event.value`.
        """
        item = event.value
        self._display_item(item)

    def _display_item(self, item: GroupLayer | GroupLayerNode | None):
        if item is None:
            self.setCurrentWidget(self.empty_widget)
        else:
            controls = self.widgets[item]
            self.setCurrentWidget(controls)

    def _remove(self, event: Event):
        """Remove the controls target item from the list of control widgets.

        Parameters
        ----------
        event : Event
            Event with the target item at `event.value`.
        """
        item = event.value
        controls = self.widgets[item]
        self.removeWidget(controls)
        controls.hide()
        controls.deleteLater()
        controls = None
        del self.widgets[item]
