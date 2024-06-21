from __future__ import annotations

import random
import string
from typing import Optional

from napari.layers import Layer
from napari.utils.tree import Group

from napari_experimental.group_layer_node import GroupLayerNode


def random_string(str_length: int = 5) -> str:
    return "".join(
        random.choices(string.ascii_uppercase + string.digits, k=str_length)
    )


class GroupLayer(Group[GroupLayerNode], GroupLayerNode):
    """
    GroupLayers are the "complex" component of the Tree structure that is used
    to organise Layers into Groups. A GroupLayer contains GroupLayerNodes and
    other GroupLayers (which are, in particular, a subclass of GroupLayerNode).
    """

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    def __init__(
        self,
        *items_to_include: Layer | GroupLayerNode | GroupLayer,
    ):
        # Python seems to understand that since GroupLayerNode inherits from
        # Node, and Group also inherits from Node, that GroupLayerNode
        # "wins".
        # We have to be careful about calling super() on methods inherited from
        # Node though.
        GroupLayerNode.__init__(self, layer_ptr=None)
        assert self.layer is None, (
            "GroupLayers do not track individual "
            "layers through the .layer property."
        )

        items_after_casting_layers = [
            GroupLayerNode(item) if isinstance(item, Layer) else item
            for item in items_to_include
        ]
        assert all(
            isinstance(item, GroupLayerNode)
            for item in items_after_casting_layers
        ), (
            "GroupLayers can only contain "
            "GroupLayerNodes (or other GroupLayers)."
        )
        Group.__init__(
            self,
            children=items_after_casting_layers,
            name=random_string(),
            basetype=GroupLayerNode,
        )

    def _check_already_tracking(
        self, layer_ptr: Layer, recursive: bool = True
    ) -> bool:
        """
        Return TRUE if the layer provided is already being tracked
        by a Node in this tree.

        Layer equality is determined by the IS keyword, to confirm that
        a Node is pointing to the Layer object in memory.

        :param layer_ptr: Reference to the Layer to determine is in the
        model.
        :param recurse: If True, then all sub-trees of the tree will be checked
        for the given Layer, returning True if it is found at any depth.
        """
        for item in self:
            if not item.is_group() and item.layer is layer_ptr:
                return True
            elif item.is_group() and recursive:
                if item._check_already_tracking(layer_ptr, recursive=True):
                    return True
        return False

    def _node_name(self) -> str:
        """Will be used when rendering node tree as string."""
        return f"GL-{self.name}"

    def add_new_item(
        self,
        insert_at: Optional[int] = None,
        layer_ptr: Optional[Layer] = None,
    ) -> None:
        """
        Insert a new GroupLayerNode, or GroupLayer, into the instance.

        By default, it is assumed that a new GroupLayer is being added.
        Groups added in this way may themselves be empty.

        To add a new Node, provide the layer_ptr argument.
        Adding a new Node without providing the layer it should track is
        prohibited.
        Adding a new Node that tracks an already tracked layer is also
        prohibited.
        """
        if insert_at is None:
            insert_at = len(self)

        if layer_ptr is None:
            self.insert(insert_at, GroupLayer())
        elif isinstance(layer_ptr, Layer):
            if not self._check_already_tracking(layer_ptr):
                self.insert(insert_at, GroupLayerNode(layer_ptr=layer_ptr))
            else:
                raise ValueError(
                    f"Already tracking {layer_ptr}, "
                    "but requested a new Node for it."
                )

    def is_group(self) -> bool:
        """
        Determines if this item is a genuine Node, or a branch
        containing further nodes.

        This method is explicitly defined to ensure that we can distinguish
        between genuine GroupLayerNodes and GroupLayers when traversing the
        tree.

        Due to (necessarily) being a subclass of GroupLayerNode, it is possible
        for GroupLayer instances to have the .layer property set to track a
        Layer object. This is (currently) not intended behaviour - GroupLayers
        are not meant to track Layers themselves. However it is possible to
        manually set the layer tracker, and I can foresee a situation in the
        future where this is desirable (particularly for rendering or drawing
        purposes), so am not strictly forbidding this by overwriting the .layer
        setter.
        """
        return True  # A GroupLayer is ALWAYS a branch.

    def remove_layer_item(self, layer_ptr: Layer, prune: bool = True) -> None:
        """
        Removes (all instances of) GroupLayerNodes tracking the given
        Layer from the tree model.

        If removing a layer would result in one of the Group being empty,
        then the empty Group is also removed from the model.
        This can be toggled with the `prune` argument.

        Note that the `is` keyword is used to determine equality between
        the layer provided and the layers that are tracked by the Nodes.
        This ensures that we only remove references to layers we are
        tracking from the model, rather than removing the Layer from
        memory itself (as there may still be hanging references to it).

        :param layer_ptr: All Nodes tracking layer_ptr will be removed from
        the model.
        :param prune: If True, branches that are empty after removing the
        layer in question will also be removed.
        """
        for node in self:
            if node.is_group():
                node.remove_layer_item(layer_ptr)
                if prune and len(node) == 0:
                    self.remove(node)
            elif node.layer is layer_ptr:
                self.remove(node)
