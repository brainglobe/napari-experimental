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

    def _check_already_tracking(self, layer_ptr: Layer) -> bool:
        """
        Return TRUE if the layer provided is already being tracked
        by a Node in this tree.

        Layer equality is determined by the IS keyword, to confirm that
        a Node is pointing to the Layer object in memory.

        :param layer_ptr: Reference to the Layer to determine is in the
        model.
        """
        for tracked_layer in self:
            if (
                isinstance(tracked_layer, LayerDisplayNode)
                and tracked_layer.layer is layer_ptr
            ):
                return True
        else:
            return False

    def add_new_item(
        self,
        insert_at: Optional[int] = None,
        layer_ptr: Optional[Layer] = None,
    ) -> None:
        """
        Insert a new LayerDisplayNode, or LayerNamesTracker, into the instance.

        By default, it is assumed that a new LayerNamesTracker (Group)
        is being added. Groups added in this way may themselves be empty.

        To add a new Node, provide the layer_ptr argument.
        Adding a new Node without providing the layer it should track is
        prohibited.
        Adding a new Node that tracks an already tracked layer is also
        prohibited.
        """
        if insert_at is None:
            insert_at = len(self)

        if layer_ptr is None:
            self.insert(insert_at, LayerNamesTracker())
        elif isinstance(layer_ptr, Layer):
            if not self._check_already_tracking(layer_ptr):
                self.insert(insert_at, LayerDisplayNode(layer_ptr=layer_ptr))
            else:
                raise ValueError(
                    f"Already tracking {layer_ptr}, "
                    "but requested a new Node for it."
                )

    def remove_layer_item(self, layer_ptr: Layer, prune: bool = True) -> None:
        """
        Removes the LayerDisplayNode item tracking (all instances of)
        the given Layer from the tree model.

        If removing a layer would result in one of the branches of the
        tree being barren, then the empty branch is also removed from
        the model. This can be toggled with the prune argument.

        Note that the IS keyword is used to determine equality between
        the layer provided and the layers that are tracked by the Nodes.
        This ensures that we only remove references to layers we are
        tracking from the model, rather than removing the Layer from
        memory itself (as there may still be hanging references to it).

        :param layer_ptr: All Nodes tracking layer_ptr will be removed from
        the model.
        :param prune: If True, branches that are empty after removing the
        layer in question will also be removed.
        """
        for tracked_layer in self:
            if isinstance(tracked_layer, LayerNamesTracker):
                tracked_layer.remove_layer_item(layer_ptr)
                if prune and len(tracked_layer) == 0:
                    self.remove(tracked_layer)
            elif tracked_layer.layer is layer_ptr:
                self.remove(tracked_layer)


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