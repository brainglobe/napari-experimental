from __future__ import annotations

from typing import Optional

from napari.layers import Layer
from napari.utils.tree import Node


class GroupLayerNode(Node):
    """
    A Node item for a tree-like data structure that has a dedicated attribute
    for tracking a single Layer. See `napari.utils.tree` for more information
    about Nodes.

    GroupLayerNodes are the core building block of the GroupLayer display. By
    wrapping a Layer inside a Node in this way, Layers can be organised into a
    tree-like structure (allowing for grouping and nesting) without the hassle
    of subclassing or mixing-in the Node class (which would require widespread
    changes to the core napari codebase).

    Parameters
    ----------
    layer_ptr : Layer, optional
        The Layer object that this Node should initially track.
    name: str, optional
        Name to be given to the Node upon creation. The Layer retains its name.
    """

    __default_name: str = "Node[None]"

    _tracking_layer: Layer | None

    @property
    def is_tracking(self) -> bool:
        """
        Returns True if the Node is currently tracking a Layer
        (self.Layer is not None), else False.
        """
        return self.layer is not None

    @property
    def layer(self) -> Layer:
        """
        The (pointer to the) Layer that the Node is currently tracking.
        """
        return self._tracking_layer

    @layer.setter
    def layer(self, new_ptr: Layer) -> None:
        assert (
            isinstance(new_ptr, Layer) or new_ptr is None
        ), f"{type(new_ptr)} is not a layer or None!"
        self._tracking_layer = new_ptr

    @property
    def name(self) -> str:
        """
        Name of the Node.

        If the Node is tracking a Layer, returns the name of the Layer.
        Otherwise, returns the internal name of the Node.
        """
        if self.is_tracking:
            return self.layer.name
        else:
            return self.__default_name

    @name.setter
    def name(self, value: str) -> None:
        if self.is_tracking:
            self.layer.name = value

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
