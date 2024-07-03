from __future__ import annotations

import random
import string
from typing import Optional

from napari.layers import Layer
from napari.utils.events import Event
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

    @property
    def visible(self):
        return self._visible

    @visible.setter
    def visible(self, value: bool) -> None:
        for item in self.traverse():
            if item.is_group():
                item._visible = value
            else:
                item.layer.visible = value
        self._visible = value

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

        # If selection changes on this node, propagate changes to any children
        self.selection.events.changed.connect(self.propagate_selection)

        # Default to group being visible
        self._visible = True

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
        :param recursive: If True, then all sub-trees of the tree will be
        checked for the given Layer, returning True if it is found at any
        depth.
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

    def propagate_selection(
        self,
        event: Optional[Event] = None,
        new_selection: Optional[list[GroupLayer | GroupLayerNode]] = None,
    ) -> None:
        """
        Propagate selection from this node to all its children. This is
        necessary to keep the .selection consistent at all levels in the tree.

        This prevents scenarios where e.g. a tree like
        Root
        - Points_0
          - Group_A
          - Points_A0
        could have Points_A0 selected on Root (appearing in its .selection),
        but not on Group_A (not appearing in its .selection)

        Parameters
        ----------
        event: selection changed event that triggers this propagation
        new_selection: List of group layer / group layer node to be selected.
            If none, it will use the current selection on this node.
        """
        if new_selection is None:
            new_selection = self.selection

        self.selection.intersection_update(new_selection)
        self.selection.update(new_selection)

        for g in [group for group in self if group.is_group()]:
            # filter for things in this group
            relevent_selection = [node for node in new_selection if node in g]
            g.propagate_selection(event=None, new_selection=relevent_selection)
