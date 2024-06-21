from napari._qt.layer_controls import QtLayerControlsContainer
from napari._qt.layer_controls.qt_layer_controls_container import (
    create_qt_layer_controls,
)
from napari.utils.events import Event
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QFrame, QHBoxLayout, QLabel

from napari_experimental.group_layer import GroupLayer, NodeWrappingLayer


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

    def __init__(self, viewer, group_layers) -> None:
        super().__init__(viewer)

        # Disconnect controls from any layer events from the viewer -
        # we want to only use events from group_layers
        self.viewer.layers.events.inserted.disconnect(self._add)
        self.viewer.layers.events.removed.disconnect(self._remove)
        self.viewer.layers.selection.events.active.disconnect(self._display)

        for node in group_layers:
            # TODO - needs to recurse into groups
            event = Event(type_name="inserted")
            event.value = node
            self._add(event)

        # Respond to changes in group layers
        group_layers.events.inserted.connect(self._add)
        group_layers.events.removed.connect(self._remove)
        group_layers.selection.events.active.connect(self._display)

    def _add(self, event):
        """Add the controls target node to the list of control widgets.

        Parameters
        ----------
        event : Event
            Event with the target node at `event.value`.
        """
        node = event.value
        if isinstance(node, NodeWrappingLayer):
            layer = event.value.layer
            controls = create_qt_layer_controls(layer)
        elif isinstance(node, GroupLayer):
            controls = QtGroupLayerControls()

        controls.ndisplay = self.viewer.dims.ndisplay
        self.addWidget(controls)
        self.widgets[node] = controls

    def _display(self, event):
        """Change the displayed controls to be those of the target node.

        Parameters
        ----------
        event : Event
            Event with the target node at `event.value`.
        """
        node = event.value
        if node is None:
            self.setCurrentWidget(self.empty_widget)
        else:
            controls = self.widgets[node]
            self.setCurrentWidget(controls)

    def _remove(self, event):
        """Remove the controls target node from the list of control widgets.

        Parameters
        ----------
        event : Event
            Event with the target node at `event.value`.
        """
        node = event.value
        controls = self.widgets[node]
        self.removeWidget(controls)
        controls.hide()
        controls.deleteLater()
        controls = None
        del self.widgets[node]
