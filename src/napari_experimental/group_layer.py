from __future__ import annotations

import random
import string
from collections import defaultdict
from typing import Dict, Iterable, List, Literal, Optional

from napari.layers import Layer
from napari.utils.events import Event
from napari.utils.events.containers._nested_list import (
    NestedIndex,
    split_nested_index,
)
from napari.utils.translations import trans
from napari.utils.tree import Group

from napari_experimental.group_layer_node import GroupLayerNode


def random_string(str_length: int = 5) -> str:
    return "".join(
        random.choices(string.ascii_uppercase + string.digits, k=str_length)
    )


class GroupLayer(Group[GroupLayerNode], GroupLayerNode):
    """
    A Group item for a tree-like data structure whose nodes have a dedicated
    attribute for tracking a single Layer. See ``napari.utils.tree`` for more
    information about Nodes and Groups.

    GroupLayers are the "complex" component of the Tree structure that is used
    to organise Layers into Groups. A GroupLayer contains GroupLayerNodes and
    other GroupLayers (which are, in particular, a subclass of GroupLayerNode).
    By convention, GroupLayers themselves do not track individual Layers, and
    hence their ``.layer`` property is always set to ``None``. Contrastingly,
    their ``.is_group()`` method always returns ``True`` compared to a
    GroupLayerNode's method returning ``False``.

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

    __next_uid: int = -1
    _uid: int

    @property
    def name(self) -> str:
        """
        Name of the GroupLayer.
        """
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

    @property
    def uid(self) -> int:
        """
        Unique ID of this instance of GroupLayer.
        Assigned on instantiation and cannot be overwritten.
        """
        return self._uid

    def __eq__(self, other: GroupLayer) -> bool:
        """
        GroupLayers are only equal if we are pointing to the same object.
        """
        return isinstance(other, GroupLayer) and self.uid == other.uid

    def __hash__(self) -> int:
        """
        Since GroupLayers are assigned a unique ID on creation, we can use
        this value as the hash of a particular instance.
        """
        return self._uid

    def __init__(
        self,
        *items_to_include: Layer | GroupLayerNode | GroupLayer,
    ):
        # Assign me a unique uid
        self._uid = GroupLayer._next_uid()
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

    @classmethod
    def _next_uid(cls) -> int:
        """
        Return the next free unique ID that can be assigned to an instance of
        this class, then increment the counter to the next available index.
        """
        cls.__next_uid += 1
        return cls.__next_uid

    @staticmethod
    def _revise_indices_based_on_previous_moves(
        original_index: NestedIndex,
        original_dest: NestedIndex,
        previous_moves: Dict[NestedIndex, List[int]],
    ) -> NestedIndex:
        """
        Intended for use during the multi_move process.
        Given an index referencing a position in the tree prior to the
        start of a multi-move, return the new index of the original
        object that was referenced.

        Parameters
        ----------
        original_index : NestedIndex
            The original index of the item in the tree.
        original_dest : NestedIndex
            The original destination index of the item.
        previous_moves : Dict[NestedIndex, List[int]]
            A dictionary whose keys are indices of groups that have had items
            moved prior to this one, and whose values are the indices in that
            group which were moved. All indices (for Groups and Nodes) should
            use the original indexing convention (prior to the application of
            any moves).
        """
        moves_prior_to_this_one = sum(
            len(list_of_indices) for list_of_indices in previous_moves.values()
        )
        revised_index = list(original_index)
        for ii in range(len(revised_index)):
            examining = original_index[: ii + 1]
            nested_group_ind, nested_ind = split_nested_index(examining)
            old_position_in_this_group = nested_ind

            if nested_group_ind in previous_moves:
                # Every move that took out an item above this one will decrease
                # the effective index by 1
                nested_ind -= sum(
                    1
                    for index in previous_moves[nested_group_ind]
                    if index < old_position_in_this_group
                )
            # If this item lives in the same group as the destination index,
            # and it is BELOW or AT the destination index, it will now have
            # moved down a number of indices equal to the number of previous
            # moves.
            orig_dest_group_ind, orig_dest_ind = split_nested_index(
                original_dest
            )
            if (
                nested_group_ind == orig_dest_group_ind
                and old_position_in_this_group >= orig_dest_ind
            ):
                nested_ind += moves_prior_to_this_one

            # Update this part of the group index with its new position
            revised_index[ii] = nested_ind
        return tuple(revised_index)

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

    def _move_plan(
        self, sources: Iterable[NestedIndex], dest_index: NestedIndex
    ):
        """Prepare indices for a multi-move.

        Given a set of ``sources`` from anywhere in the list,
        and a single ``dest_index``, this function computes and yields
        ``(from_index, to_index)`` tuples that can be used sequentially in
        single move operations.  It keeps track of what has moved where and
        updates the source and destination indices to reflect the model at each
        point in the process.

        This is useful for a drag-drop operation with a QtModel/View.

        Parameters
        ----------
        sources : Iterable[NestedIndex]
            An iterable of NestedIndex that should be moved to ``dest_index``.
        dest_index : Tuple[int]
            The destination for sources.
        """
        if isinstance(dest_index, slice):
            raise TypeError(
                trans._(
                    "Destination index may not be a slice",
                    deferred=True,
                )
            )

        to_move: List[NestedIndex] = []
        for idx in sources:
            if isinstance(idx, tuple):
                to_move.append(idx)
            elif isinstance(idx, int):
                to_move.append((idx,))
            elif isinstance(idx, slice):
                raise NotImplementedError(
                    "Slices should not be sent to a "
                    "GroupLayer when multi-moving"
                )
                to_move.extend(list(range(*idx.indices(len(self)))))
            else:
                raise TypeError(
                    trans._(
                        "Can only move NestedIndices indices and ints which "
                        "can be cast to NestedIndices, not {t}",
                        deferred=True,
                        t=type(idx),
                    )
                )

        # (Relative) flat index order must be preserved when moving multiple
        # items, so sort the order of the sources here to ensure consistency.
        flat_order = self.flat_index_order(include_groups=True)
        to_move = sorted(to_move, key=lambda x: flat_order.index(x))

        dest_group_ind, dest_ind = split_nested_index(dest_index)
        dest_group = self[dest_group_ind]
        assert dest_group.is_group()
        if dest_ind < 0:
            dest_ind += len(dest_group) + 1
            dest_index = dest_group_ind + (dest_ind,)
        # dest_group_ind + (dest_ind,) is now the target insertion point for
        # the first item.

        previous_moves = defaultdict(list)
        for src in to_move:
            revised_source = self._revise_indices_based_on_previous_moves(
                original_index=src,
                original_dest=dest_index,
                previous_moves=previous_moves,
            )
            revised_dest = self._revise_indices_based_on_previous_moves(
                original_index=dest_index,
                original_dest=dest_index,
                previous_moves=previous_moves,
            )
            yield revised_source, revised_dest

            # Record that a move occurred in the source group.
            # Note that the sum of the lengths of the values of this
            # dict is equal to the number of moves in the multi-move
            # we have done so far.
            previous_moves[src[:-1]].append(src[-1])

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
                item: GroupLayer
                if item.check_already_tracking(layer_ptr, recursive=True):
                    return True
        return False

    def flat_index_order(
        self, include_groups: bool = False
    ) -> List[NestedIndex]:
        """
        Return a list of NestedIndex-es, whose order corresponds to
        the flat order of the Nodes in the tree.

        The flat order of the Nodes counts up from 0 at the root of the
        tree, and descends down into the tree, exhausting branches it
        encounters before continuing.

        For the tree below;

        * Node_0
        * Node_1
        * Group_A
            * Node_A0
            * Node_A1
            * Group_AA
                * Node_AA0
            * Node_A2
        * Node_2

        we have the following flat order and corresponding indices:

        ========  ==========  ==================
        Item      Flat Index  ``include_groups``
        ========  ==========  ==================
        Node_0    0           0
        Node_1    1           1
        Group_A   n/a         2
        Node_A0   2           3
        Node_A1   3           4
        Group_AA  n/a         5
        Node_AA0  4           6
        Node_A2   5           7
        Node_2    6           8
        ========  ==========  ==================

        Parameters
        ----------
        include_groups : bool, default = False
            Whether to assign groups their own place in the order,
            or to skip over them.
        """
        order: List[NestedIndex] = []
        for item in self:
            if item.is_group():
                # This is a group, descend into it and append
                # its ordering to our current ordering
                item: GroupLayer
                if include_groups:
                    order.append(item.index_from_root())
                order += item.flat_index_order(include_groups=include_groups)
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

    def propagate_selection(
        self,
        event: Optional[Event] = None,
        new_selection: Optional[list[GroupLayer | GroupLayerNode]] = None,
    ) -> None:
        """
        Propagate selection from this node to all its children. This is
        necessary to keep the .selection consistent at all levels in the tree.

        This prevents scenarios where e.g. a tree like

        * ``Root``
            * ``Points_0``
                * ``Group_A``
                * ``Points_A0``

        could have ``Points_A0`` selected on ``Root`` (appearing in its
        ``.selection``), but not on ``Group_A`` (not appearing in its
        ``.selection``).

        Parameters
        ----------
        event: Event, optional
            Selection changed event that triggers this propagation
        new_selection: list[GroupLayer | GroupLayerNode], optional
            List of group layer / group layer node to be selected.
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
