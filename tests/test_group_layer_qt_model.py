from typing import Tuple

import pytest
from napari_experimental.group_layer import GroupLayer
from napari_experimental.group_layer_qt import QtGroupLayerModel
from qtpy.QtCore import QModelIndex


@pytest.fixture(scope="function")
def nested_model(nested_layer_group: GroupLayer) -> QtGroupLayerModel:
    return QtGroupLayerModel(nested_layer_group)


@pytest.fixture(scope="function")
def flat_model(group_layer_data: GroupLayer) -> QtGroupLayerModel:
    return QtGroupLayerModel(group_layer_data)


def test_qt_group_layer_model(nested_model, flat_model, qtmodeltester) -> None:
    flat = QtGroupLayerModel(root=flat_model)
    qtmodeltester.check(flat)

    nested = QtGroupLayerModel(root=nested_model)
    qtmodeltester.check(nested)


def test_iter_and_traverse(
    nested_model: QtGroupLayerModel,
    nested_layer_group: GroupLayer,
) -> None:
    """
    Test that requesting i in QtGroupLayerModel iterates through the
    valid model indices, using the traverse method.

    Validate that the returned indices match 1:1 with the underlying
    data structure objects.
    """
    generated_items = [index for index in nested_model]

    assert len(generated_items) == nested_layer_group.n_items_in_tree, (
        "Did not generate correct number of indices "
        f"(got {len(generated_items)}, "
        f"expected {nested_layer_group.n_items_in_tree})."
    )

    all_tree_items = [item for item in nested_layer_group]
    all_group_items = []
    while any(item.is_group() for item in all_tree_items):
        for group_item in [item for item in all_tree_items if item.is_group()]:
            all_tree_items.remove(group_item)
            all_group_items.append(group_item)
            all_tree_items += [item for item in group_item]

    for index in generated_items:
        assert isinstance(index, QModelIndex)

        item = nested_model.getItem(index)
        if item.is_group():
            assert item in all_group_items
        else:
            assert item in all_tree_items


@pytest.mark.parametrize(
    ["nested_index_of_item", "expected_flat_index"],
    [
        pytest.param((0,), 0, id="Points_0"),
        pytest.param((1,), 1, id="Group_A"),
        pytest.param((1, 0), 2, id="Points_A0"),
        pytest.param((1, 1), 3, id="Group_AA"),
        pytest.param((1, 1, 0), 4, id="Points_AA0"),
        pytest.param((1, 1, 1), 5, id="Group_AA1"),
        pytest.param((1, 2), 6, id="Points_A1"),
        pytest.param((2,), 7, id="Points_1"),
        pytest.param((3,), 8, id="Group_B"),
        pytest.param((3, 0), 9, id="Points_B0"),
    ],
)
def test_flatindex_to_index(
    nested_model: QtGroupLayerModel,
    nested_index_of_item: Tuple[int, ...],
    expected_flat_index: int,
) -> None:
    """
    Using the structure of the nested_layer_group model, check that the flat
    index-es map to the correct model items.

    Recall the structure of the nested_layer_group fixture for explanation of
    the parametrisation.
    """
    assert (
        nested_model.nestedIndex(nested_index_of_item)
        == nested_model.flatindex_to_index[expected_flat_index]
    )
