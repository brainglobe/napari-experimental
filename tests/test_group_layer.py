from typing import Callable, Dict

import pytest
from napari.layers import Points
from napari.utils.events.containers._nested_list import NestedIndex
from napari_experimental.group_layer import GroupLayer
from napari_experimental.group_layer_node import GroupLayerNode

from .fixtures.conftest_layers import return_copy_with_new_name


def recursively_apply_function(
    group_layer: GroupLayer, func: Callable[[GroupLayer], None]
) -> None:
    """
    Recursively apply a function to all members of a GroupLayer, and then all
    subtrees of that GroupLayer. Functions are intended to conduct the
    necessary assertions for a particular test.
    """
    func(group_layer)

    for branch in [
        item for item in group_layer if isinstance(item, GroupLayer)
    ]:
        recursively_apply_function(branch, func)


def test_group_layer_types(nested_layer_group: GroupLayer) -> None:
    """
    Check that everything stored in a GroupLayer is a GroupLayerNode,
    and that any child GroupLayers also adhere to this structure.
    """

    def assert_correct_types(group_layer: GroupLayer) -> None:
        assert isinstance(
            group_layer, GroupLayer
        ), f"{group_layer} is not a GroupLayer instance."

        for item in group_layer:
            assert isinstance(
                item, GroupLayerNode
            ), f"{item} in {group_layer} is not a GroupLayerNode instance."

    recursively_apply_function(nested_layer_group, assert_correct_types)


def test_is_group(nested_layer_group: GroupLayer) -> None:
    """
    Check that GroupLayer instances always return True
    from their is_group() method.
    """

    def assert_correct_is_group(group_layer: GroupLayer) -> None:
        assert (
            group_layer.is_group()
        ), f"{group_layer} is not flagged as a Group."

        for node in [
            item for item in group_layer if not isinstance(item, GroupLayer)
        ]:
            assert not node.is_group()

    recursively_apply_function(nested_layer_group, assert_correct_is_group)


@pytest.mark.parametrize(
    ["layer_key", "recursive", "expected_result"],
    [
        pytest.param("A0", True, True, id="Depth 1, recurse True"),
        pytest.param("AA0", True, True, id="Depth 2, recurse True"),
        pytest.param("A0", False, False, id="Depth 1, recurse False"),
        pytest.param("1", False, True, id="Depth 0, recurse False"),
    ],
)
def test_check_is_already_tracking(
    nested_layer_group: GroupLayer,
    collection_of_layers: Dict[str, Points],
    layer_key: str,
    recursive: bool,
    expected_result: bool,
):
    assert (
        nested_layer_group._check_already_tracking(
            layer_ptr=collection_of_layers[layer_key], recursive=recursive
        )
        == expected_result
    ), (
        f"Incorrect result (expected {expected_result}) "
        f"for _check_already_tracking (with recursive = {recursive})"
    )


def test_flat_index(nested_layer_group: GroupLayer) -> None:
    """
    - Points_0
    - Group_A
      - Points_A0
      - Group_AA
        - Points_AA0
        - Points_AA1
      - Points_A1
    - Points_1
    - Group_B
      - Points_B0
    """
    flat_order = nested_layer_group.flat_index_order()
    expected_flat_order = [
        (0,),  # Points_0
        (1, 0),  # Points_A0
        (1, 1, 0),  # Points_AA0
        (1, 1, 1),  # Points_AA1
        (1, 2),  # Points_A1
        (2,),  # Points_1
        (3, 0),  # Points_B0
    ]
    for i, returned_nested_index in enumerate(flat_order):
        expected_nested_index = expected_flat_order[i]
        assert expected_nested_index == returned_nested_index, (
            f"Mismatch at position {i}: "
            f"got {returned_nested_index} but expected {expected_nested_index}"
        )


@pytest.mark.parametrize(
    ["location", "expected_location"],
    [
        pytest.param(None, (-1), id="Default location"),
        pytest.param((1, 1), (1, 1), id="Inside a sub-Group"),
    ],
)
def test_add_layer(
    nested_layer_group: GroupLayer,
    points_layer: Points,
    location: NestedIndex,
    expected_location: NestedIndex,
) -> None:
    nested_layer_group.add_new_layer(points_layer, location=location)
    assert nested_layer_group[expected_location].layer == points_layer, (
        f"Layer was not inserted at {expected_location} "
        f"(given location argument {location})."
    )


def test_add_layer_failure_cases(
    nested_layer_group: GroupLayer, points_layer: Points
) -> None:
    # Cannot add a Layer to a Node object - target must be a space in a Group
    pts_added_to_a_node = return_copy_with_new_name(
        points_layer, "Add to a Node"
    )
    with pytest.raises(
        ValueError,
        match="Item at (.*) is not a Group",
    ):
        nested_layer_group.add_new_layer(pts_added_to_a_node, (1, 0, 1))

    # Must provide a Layer pointer to create a new Node
    with pytest.raises(
        ValueError,
        match="A Layer must be provided when (.*)",
    ):
        nested_layer_group.add_new_layer(None)

    # Cannot track the same Layer twice
    nested_layer_group.add_new_layer(points_layer)  # Add the layer
    with pytest.raises(
        RuntimeError, match="Group Node\[.*\] is already tracking"
    ):
        nested_layer_group.add_new_layer(points_layer)  # Try to add it again


def test_add_group(
    nested_layer_group: GroupLayer,
    points_layer: Points,
) -> None:
    add_at_location = (2,)
    pts_1 = return_copy_with_new_name(points_layer, "pts_1")
    pts_2 = return_copy_with_new_name(points_layer, "pts_2")

    nested_layer_group.add_new_group(pts_1, pts_2, location=add_at_location)

    assert nested_layer_group[
        add_at_location
    ].is_group(), "Group added in the incorrect location."

    added_group: GroupLayer = nested_layer_group[add_at_location]
    assert added_group._check_already_tracking(
        pts_1
    ) and added_group._check_already_tracking(
        pts_2
    ), "Points layers were not added to the new Group upon creation."
    assert (
        len(added_group) == 2
    ), "Additional items added to the Group upon creation."
