from copy import deepcopy
from typing import Any

import pytest
from napari_experimental.group_layer import GroupLayer


def return_copy_with_new_name(obj: Any, new_name: str = "Copy") -> Any:
    """
    Returns a copy of the object that is passed with the name
    attribute set to the new name provided.
    If an object does not have a name attribute, this method
    will add one to the returned copy.
    """
    copy = deepcopy(obj)
    copy.name = new_name
    return copy


@pytest.fixture(scope="function")
def group_layer_data(points_layer, image_layer) -> GroupLayer:
    return GroupLayer(points_layer, image_layer)


@pytest.fixture(scope="function")
def nested_group_data(points_layer) -> GroupLayer:
    """
    Creates a GroupLayer container with the following structure:

    Root
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
    points_aa0 = return_copy_with_new_name(points_layer, "Points_AA0")
    points_aa1 = return_copy_with_new_name(points_layer, "Points_AA1")
    group_aa = GroupLayer(points_aa0, points_aa1)

    points_a0 = return_copy_with_new_name(points_layer, "Points_A0")
    points_a1 = return_copy_with_new_name(points_layer, "Points_A1")
    group_a = GroupLayer(points_a0, group_aa, points_a1)

    points_b0 = return_copy_with_new_name(points_layer, "Points_B0")
    group_b = GroupLayer(points_b0)

    points_0 = return_copy_with_new_name(points_layer, "Points_0")
    points_1 = return_copy_with_new_name(points_layer, "Points_1")

    root = GroupLayer(points_0, group_a, points_1, group_b)
    return root
