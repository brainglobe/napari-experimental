from typing import TYPE_CHECKING

from napari._qt.layer_controls import QtLayerControlsContainer
from napari._qt.layer_controls.qt_layer_controls_container import (
    create_qt_layer_controls,
)
from napari.utils.events import Event
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QFrame, QHBoxLayout, QLabel

from napari_experimental.group_layer import GroupLayer

if TYPE_CHECKING:
    import napari


class QtGroupLayerControls(QFrame):

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

        for item in group_layers:
            # TODO - needs to recurse into groups
            event = Event(type_name="inserted")
            event.value = item
            self._add(event)

        # Respond to changes in group layers
        group_layers.events.inserted.connect(self._add)
        group_layers.events.removed.connect(self._remove)
        group_layers.selection.events.active.connect(self._display)

    def _add(self, event: Event):
        """Add the controls target item to the list of control widgets.

        Parameters
        ----------
        event : Event
            Event with the target item at `event.value`.
        """
        item = event.value
        if item.is_group():
            controls = QtGroupLayerControls()
        else:
            layer = event.value.layer
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
