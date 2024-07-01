from __future__ import annotations

import random
import string
from collections import defaultdict
from typing import Dict, Iterable, List, Optional

from napari.layers import Layer
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

    def _revise_indices_based_on_previous_moves(
        self,
        original_index: NestedIndex,
        original_dest: NestedIndex,
        previous_moves: Dict[NestedIndex, List[int]],
        moves_prior_to_this_one: int,
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
            group which were moved. Group indices (keys) should use indices
            from the original tree structure. The values however need to use
            the updated position within the groups (accounting for previous
            moves).
        moves_prior_to_this_one: int
            Number of moves in the multi move that have been carried out prior
            to this one.
        """
        revised_index = list(original_index)
        for ii in range(len(revised_index)):
            examining = original_index[: ii + 1]
            nested_group_ind, nested_ind = split_nested_index(examining)

            if nested_group_ind in previous_moves.keys():
                # There has previous been at least 1 item moved around
                # in this group prior to this move.
                nested_ind -= sum(
                    1
                    for index in previous_moves[nested_group_ind]
                    if index < nested_ind
                )
            orig_dest_group_ind, orig_dest_ind = split_nested_index(
                original_dest
            )
            if (
                nested_group_ind == orig_dest_group_ind
                and nested_ind >= orig_dest_ind
            ):
                nested_ind += moves_prior_to_this_one
            # Update this part of the group index with its new position
            revised_index[ii] = nested_ind
        return tuple(revised_index)

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

    def _move_plan(
        self, sources: Iterable[NestedIndex], dest_index: NestedIndex
    ):
        """Prepared indices for a multi-move.

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
                to_move.extend(list(range(*idx.indices(len(self)))))
                raise NotImplementedError("Should never hit this case?")
            else:
                raise TypeError(
                    trans._(
                        "Can only move integer or slice indices, not {t}",
                        deferred=True,
                        t=type(idx),
                    )
                )

        dest_group_ind, dest_ind = split_nested_index(dest_index)
        dest_group = self[dest_group_ind]
        assert dest_group.is_group()
        if dest_ind < 0:
            dest_ind += len(dest_group) + 1
            dest_index = dest_group_ind + (dest_ind,)
        # dest_group_ind + (dest_ind,) is now the target insertion point for
        # the first item.

        previous_moves = defaultdict(list)
        objects_moved_up = 0
        for n_previous_insertions, src in enumerate(to_move):
            revised_source = self._revise_indices_based_on_previous_moves(
                original_index=src,
                original_dest=dest_index,
                previous_moves=previous_moves,
                moves_prior_to_this_one=n_previous_insertions,
            )
            revised_dest = self._revise_indices_based_on_previous_moves(
                original_index=dest_index,
                original_dest=dest_index,
                previous_moves=previous_moves,
                moves_prior_to_this_one=n_previous_insertions,
            )
            yield revised_source, revised_dest

            # Record that a move occurred in the source group
            previous_moves[src[:-1]].append(revised_source[-1])

            # Account for moving items above the destination index.
            rev_src_grp, rev_src_ind = split_nested_index(revised_source)
            rev_dst_grp, rev_dst_ind = split_nested_index(revised_dest)
            if rev_src_grp == rev_dst_grp and rev_dst_ind <= rev_src_ind:
                objects_moved_up += 1

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
