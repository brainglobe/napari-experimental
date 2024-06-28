from __future__ import annotations

import random
import string
from typing import Iterable, List, Literal, Optional

from napari.layers import Layer
from napari.utils.events.containers._nested_list import (
    NestedIndex,
    split_nested_index,
)
from napari.utils.tree import Group

from napari_experimental.group_layer_node import GroupLayerNode


def random_string(str_length: int = 5) -> str:
    return "".join(
        random.choices(string.ascii_uppercase + string.digits, k=str_length)
    )


class GroupLayer(Group[GroupLayerNode], GroupLayerNode):
    """
    A Group item for a tree-like data structure whose nodes have a dedicated
    attribute for tracking a single Layer. See `napari.utils.tree` for more
    information about Nodes and Groups.

    GroupLayers are the "complex" component of the Tree structure that is used
    to organise Layers into Groups. A GroupLayer contains GroupLayerNodes and
    other GroupLayers (which are, in particular, a subclass of GroupLayerNode).
    By convention, GroupLayers themselves do not track individual Layers, and
    hence their `.layer` property is always set to `None`. Contrastingly, their
    `.is_group()` method always returns `True` compared to a `GroupLayerNode`'s
    method returning `False`.

    Since the Nodes in the tree map 1:1 with the Layers, the docstrings and
    comments within this class often use the words interchangeably. This may
    give rise to phrases such as "Layers in the model" even though - strictly
    speaking - there are no Layers in the model, only GroupLayerNodes which
    track the Layers. Such phrases should be taken to mean "Layers which are
    tracked by one GroupLayerNode in the model", and typically serve to save on
    the verbosity of comments. In places where this may give rise to ambiguity,
    the precise language is used.

    Parameters
    ----------
    *items_to_include : Layer | GroupLayerNode | GroupLayer
        Items to be added (in the order they are given as arguments) to the
        Group when it is instantiated. Layers will have a Node created to
        track them, GroupLayerNodes will simply be added to the GroupLayer,
        as will other GroupLayers.
    """

    @property
    def name(self) -> str:
        """
        Name of the GroupLayer.
        """
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

    def _add_new_item(
        self,
        item_type: Literal["Node", "Group"],
        location: Optional[NestedIndex | int] = None,
        layer_ptr: Optional[Layer] = None,
        group_items: Optional[
            Iterable[Layer | GroupLayer | GroupLayerNode]
        ] = None,
    ) -> None:
        """
        Abstract method handling the addition of Nodes and Groups to the
        tree structure. See also `add_new_layer` and `add_new_group`.

        Parameters
        ----------
        item_type: Literal
            The type of item to add to the tree.
            Must be one of: "Node", "Group".
        location: NestedIndex | int, optional
            Location in the tree to insert the new item.
            Items are added to the end of the top level of the tree by default.
        layer_ptr: Layer, optional
            If creating a new Node, the Layer that the Node should track.
        group_items: Iterable[GroupLayer | GroupLayerNode], optional
            If creating a new Group, the items that should be added to said
            Group upon its creation.
        """
        if item_type not in ["Node", "Group"]:
            raise ValueError(
                f"Unknown item type to insert into Tree: {item_type} "
                "(expected 'Node' or 'Group')"
            )
        if location is None:
            location = ()
        insert_to_group, insertion_index = split_nested_index(location)

        insertion_group = (
            self if not insert_to_group else self[insert_to_group]
        )
        if not insertion_group.is_group():
            raise ValueError(
                f"Item at {insert_to_group} is not a Group, "
                "so cannot have an item inserted!"
            )
        if insertion_index == -1:
            insertion_index = len(insertion_group)

        if item_type == "Node":
            if layer_ptr is None:
                raise ValueError(
                    "A Layer must be provided when "
                    "adding a Node to the GroupLayers tree."
                )
            elif insertion_group.check_already_tracking(layer_ptr=layer_ptr):
                raise RuntimeError(
                    f"Group {insertion_group} is already tracking {layer_ptr}"
                )
            insertion_group.insert(
                insertion_index, GroupLayerNode(layer_ptr=layer_ptr)
            )
        elif item_type == "Group":
            if group_items is None:
                group_items = ()
            insertion_group.insert(insertion_index, GroupLayer(*group_items))

    def _node_name(self) -> str:
        """Will be used when rendering node tree as string."""
        return f"GL-{self.name}"

    def add_new_layer(
        self,
        layer_ptr: Layer,
        location: Optional[NestedIndex | int] = None,
    ) -> None:
        """
        Add a new (Node tracking a) Layer to the model.
        New Nodes are by default added at the bottom of the tree.

        Parameters
        ----------
        layer_ptr : napari.layers.Layer
            Layer to add and track with a Node
        location : NestedIndex | int, optional
            Location at which to insert the new (Node tracking the) Layer.
        """
        self._add_new_item("Node", location=location, layer_ptr=layer_ptr)

    def add_new_group(
        self,
        *items: Layer | GroupLayer | GroupLayerNode,
        location: Optional[NestedIndex | int] = None,
    ) -> None:
        """
        Add a new Group (of Layers) to the model.
        New Groups are by default added at the bottom of the tree.

        Parameters
        ----------
        location: NestedIndex | int, optional
            Location at which to insert the new GroupLayer.
        items: Layer | GroupLayer | GroupLayerNode, optional
            Items to add to the new GroupLayer upon its creation.
        """
        self._add_new_item("Group", location=location, group_items=items)

    def check_already_tracking(
        self, layer_ptr: Layer, recursive: bool = True
    ) -> bool:
        """
        Return TRUE if the Layer provided is already being tracked
        by a Node in this tree.

        Layer equality is determined by the IS keyword, to confirm that
        a Node is pointing to the Layer object in memory.

        Parameters
        ----------
        layer_ptr : Layer
            The Layer to determine is in the tree (or not).
        recursive: bool, default = True
            If True, then all sub-trees of the tree will be checked for the
            given Layer, returning True if it is found at any depth.
        """
        for item in self:
            if not item.is_group() and item.layer is layer_ptr:
                return True
            elif item.is_group() and recursive:
                if item._check_already_tracking(layer_ptr, recursive=True):
                    return True
        return False

    def flat_index_order(self) -> List[NestedIndex]:
        """
        Return a list of NestedIndex-es, whose order corresponds to
        the flat order of the Nodes in the tree.

        The flat order of the Nodes counts up from 0 at the root of the
        tree, and descends down into the tree, exhausting branches it
        encounters before continuing.

        An example is given in the tree below:

        Tree                Flat Index
        - Node_0            0
        - Node_1            1
        - Group_A           n/a
            - Node_A0       3
            - Node_A1       4
            - Group_AA      n/a
                - Node_AA0  5
            - Node_A2       6
        - Node_2            7
        """
        order: List[NestedIndex] = []
        for item in self:
            if item.is_group():
                # This is a group, descend into it and append
                # its ordering to our current ordering
                item: GroupLayer
                order += item.flat_index_order()
            else:
                # This is just a node, and it is the next one in
                # the order
                order.append(item.index_from_root())
        return order

    def is_group(self) -> bool:
        """
        Determines if this item is a genuine Node, or a branch containing
        further nodes.

        This method is explicitly defined to ensure that we can distinguish
        between genuine GroupLayerNodes and GroupLayers when traversing the
        tree.
        """
        return True  # A GroupLayer is ALWAYS a branch.

    def remove_layer_item(self, layer_ptr: Layer, prune: bool = True) -> None:
        """
        Removes (all instances of) GroupLayerNodes tracking the given
        Layer from the tree model.

        If removing a layer would result in one of the Group being empty,
        then the empty Group is also removed from the model. This can be
        toggled with the `prune` argument.

        Note that the `is` keyword is used to determine equality between
        the layer provided and the layers that are tracked by the Nodes.
        This ensures that we only remove references to layers we are
        tracking from the model, rather than removing the Layer from
        memory itself (as there may still be hanging references to it).

        Parameters
        ----------
        layer_ptr : Layer
            All Nodes tracking this Layer will be removed from the model.
        prune : bool, default = True
            If True, branches that are empty after removing the Layer in
            question will also be removed.
        """
        for node in self:
            if node.is_group():
                node.remove_layer_item(layer_ptr)
                if prune and len(node) == 0:
                    self.remove(node)
            elif node.layer is layer_ptr:
                self.remove(node)
