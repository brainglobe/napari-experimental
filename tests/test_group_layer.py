from typing import Callable

from napari_experimental.group_layer import GroupLayer
from napari_experimental.group_layer_node import GroupLayerNode


def recursively_apply_function(
    group_layer: GroupLayer, func: Callable[[GroupLayer], None]
) -> None:
    """
    Recursively apply a function to all members of a GroupLayer, and then all
    subtrees of that GroupLayer. Functions are intended to conduct the necessary
    assertions for a particular test.
    """
    func(group_layer)

    for branch in [
        item for item in group_layer if isinstance(item, GroupLayer)
    ]:
        recursively_apply_function(branch, func)


def test_group_layer_types(nested_group_data: GroupLayer) -> None:
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

    recursively_apply_function(nested_group_data, assert_correct_types)


def test_is_group(nested_group_data: GroupLayer) -> None:
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

    recursively_apply_function(nested_group_data, assert_correct_is_group)
