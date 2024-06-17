from __future__ import annotations

import random
import string
from typing import TYPE_CHECKING, Iterable, Optional

from napari._qt.containers import QtNodeTreeModel, QtNodeTreeView
from napari.layers import Layer
from napari.utils.tree import Group, Node

if TYPE_CHECKING:
    from qtpy.QtWidgets import QWidget


def random_string(k: int = 5) -> str:
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=5))


class LayerDisplayNode(Node):

    __default_name: str = "LayerDisplay"

    _tracking_layer: Layer

    @property
    def is_tracking(self) -> bool:
        return self.layer is not None

    @property
    def layer(self) -> Layer:
        return self._tracking_layer

    @layer.setter
    def layer(self, new_ptr: Layer) -> None:
        assert isinstance(
            new_ptr, (Layer, None)
        ), f"{type(new_ptr)} is not a layer!"
        self._tracking_layer = new_ptr

    @property
    def name(self) -> str:
        return self.layer.name

    def __init__(
        self,
        layer_ptr: Optional[Layer] = None,
    ):
        Node.__init__(self, name=self.__default_name)

        self.layer = layer_ptr

    def __str__(self) -> str:
        return f"LayerDisplayNode tracking {self.name}"

    def __repr__(self) -> str:
        return self.__str__()


class LayerNamesTracker(Group[LayerDisplayNode]):

    def __init__(self, current_layers: Iterable[Layer] = ()):
        Group.__init__(
            self,
            children=(LayerDisplayNode(layer) for layer in current_layers),
            name=f"LayerNamesTracker-{random_string()}",
            basetype=LayerDisplayNode,
        )

    def add_new_item(
        self,
        insert_at: Optional[int] = None,
        layer_ptr: Optional[Layer] = None,
    ) -> None:
        """
        Insert a new LayerDisplayNode, or LayerNamesTracker, into the instance.

        By default, it is assumed that a new LayerNamesTracker (Group) is being added.
        - Groups added in this way may themselves be empty.

        To add a new Node, provide the layer_ptr argument.
        - Note that it is impossible to add a new Node without providing the layer it should track.

        TODO: Ensure that layers cannot be tracked by more than one Node?
        """  # noqa: E501
        if insert_at is None:
            insert_at = len(self)

        if layer_ptr is None:
            self.insert(insert_at, LayerNamesTracker())
        else:
            self.insert(insert_at, LayerDisplayNode(layer_ptr=layer_ptr))


class QtLayerNamesTreeModel(QtNodeTreeModel[LayerNamesTracker]):

    def __init__(self, root: LayerNamesTracker, parent: QWidget = None):
        super().__init__(root, parent)
        self.setRoot(root)


class QtLayerNamesTreeView(QtNodeTreeView):
    _root: LayerNamesTracker
    model_class = QtLayerNamesTreeModel

    def __init__(self, root: LayerNamesTracker, parent: QWidget = None):
        super().__init__(root, parent)
        self.setRoot(root)
