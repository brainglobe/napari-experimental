from __future__ import annotations

from typing import Optional

from napari.layers import Layer
from napari.utils.tree import Node


class GroupLayerNode(Node):

    __default_name: str = "Node[None]"

    _tracking_layer: Layer | None

    @property
    def is_tracking(self) -> bool:
        return self.layer is not None

    @property
    def layer(self) -> Layer:
        return self._tracking_layer

    @layer.setter
    def layer(self, new_ptr: Layer) -> None:
        assert (
            isinstance(new_ptr, Layer) or new_ptr is None
        ), f"{type(new_ptr)} is not a layer or None!"
        self._tracking_layer = new_ptr

    @property
    def name(self) -> str:
        if self.is_tracking:
            return self.layer.name
        else:
            return self.__default_name

    def __init__(
        self,
        layer_ptr: Optional[Layer] = None,
        name: Optional[str] = None,
    ):
        name = name if name else self.__default_name
        Node.__init__(self, name=name)

        self.layer = layer_ptr

    def __str__(self) -> str:
        return f"Node[{self.name}]"

    def __repr__(self) -> str:
        return self.__str__()
