"""
This module contains an experimental implementation of a layers widget.
"""
from typing import TYPE_CHECKING

from qtpy.QtWidgets import QHBoxLayout, QWidget

if TYPE_CHECKING:
    import napari


from napari._qt.containers import QtLayerList
from napari.components import LayerList


class LayersWidget(QWidget):
    # your QWidget.__init__ can optionally request the napari viewer instance
    # use a type annotation of 'napari.viewer.Viewer' for any parameter
    def __init__(self, viewer: "napari.viewer.Viewer"):
        super().__init__()

        self.viewer = viewer
        self.viewer.layers.events.inserted.connect(self._on_add_layer)
        self.viewer.layers.events.removed.connect(self._on_remove_layer)

        self.layer_list = LayerList()
        qt_layer_list = QtLayerList(root=self.layer_list, parent=self)

        self.setLayout(QHBoxLayout())
        self.layout().addWidget(qt_layer_list)

    def _on_add_layer(self, event):
        self.layer_list.append(event.value)

    def _on_remove_layer(self, event):
        self.layer_list.remove(event.value)
