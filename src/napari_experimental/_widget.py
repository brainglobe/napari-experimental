"""
This module contains an experimental implementation of a layers widget.
"""
from typing import TYPE_CHECKING

from qtpy.QtWidgets import QHBoxLayout, QPushButton, QWidget

if TYPE_CHECKING:
    import napari


import numpy as np
from napari._qt.containers import QtLayerList
from napari.components import LayerList
from napari.layers import Image


class LayersWidget(QWidget):
    # your QWidget.__init__ can optionally request the napari viewer instance
    # use a type annotation of 'napari.viewer.Viewer' for any parameter
    def __init__(self, viewer: "napari.viewer.Viewer"):
        super().__init__()

        add_layer_button = QPushButton("Add a random layer")
        self.layer_list = LayerList()

        qt_layer_list = QtLayerList(root=self.layer_list, parent=self)
        self.setLayout(QHBoxLayout())
        self.layout().addWidget(qt_layer_list)
        qt_layer_list.setVisible(True)
        self.layout().addWidget(add_layer_button)
        add_layer_button.clicked.connect(self._on_click)

    def _on_click(self):
        random_image_layer = Image(np.random.random((10, 10)))
        self.layer_list.append(random_image_layer)
