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
def nested_layer_group(collection_of_layers) -> GroupLayer:
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
    group_aa = GroupLayer(
        collection_of_layers["AA0"], collection_of_layers["AA1"]
    )
    group_a = GroupLayer(
        collection_of_layers["A0"], group_aa, collection_of_layers["A1"]
    )
    group_b = GroupLayer(collection_of_layers["B0"])
    root = GroupLayer(
        collection_of_layers["0"], group_a, collection_of_layers["1"], group_b
    )
    return root
