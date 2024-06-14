"""
This module contains four napari widgets declared in
different ways:

- a pure Python function flagged with `autogenerate: true`
    in the plugin manifest. Type annotations are used by
    magicgui to generate widgets for each parameter. Best
    suited for simple processing tasks - usually taking
    in and/or returning a layer.
- a `magic_factory` decorated function. The `magic_factory`
    decorator allows us to customize aspects of the resulting
    GUI, including the widgets associated with each parameter.
    Best used when you have a very simple processing task,
    but want some control over the autogenerated widgets. If you
    find yourself needing to define lots of nested functions to achieve
    your functionality, maybe look at the `Container` widget!
- a `magicgui.widgets.Container` subclass. This provides lots
    of flexibility and customization options while still supporting
    `magicgui` widgets and convenience methods for creating widgets
    from type annotations. If you want to customize your widgets and
    connect callbacks, this is the best widget option for you.
- a `QWidget` subclass. This provides maximal flexibility but requires
    full specification of widget layouts, callbacks, events, etc.

References:
- Widget specification: https://napari.org/stable/plugins/guides.html?#widgets
- magicgui docs: https://pyapp-kit.github.io/magicgui/

Replace code below according to your needs.
"""

from typing import TYPE_CHECKING

from napari.components import LayerList
from qtpy.QtWidgets import QPushButton, QVBoxLayout, QWidget

from napari_experimental.tree_model import (
    GroupLayer,
    QtLayerTreeModel,
    QtLayerTreeView,
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

        self.group_layer = GroupLayer(self.global_layers)
        self.layer_tree_model = QtLayerTreeModel(self.group_layer, parent=self)
        self.layer_tree_view = QtLayerTreeView(self.group_layer, parent=self)
        self.layer_tree_view.setModel(self.layer_tree_model)

        self.add_group_button = QPushButton("Add empty layer group")
        self.add_group_button.clicked.connect(self._on_click)

        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.add_group_button)
        self.layout().addWidget(self.layer_tree_view)

    def _on_click(self) -> None:
        """ """
        print("Button click")
