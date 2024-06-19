import pytest
from napari_experimental.group_layer import GroupLayer
from napari_experimental.group_layer_qt import QtGroupLayerModel


@pytest.fixture(scope="function")
def group_layer_data(points_layer, image_layer) -> GroupLayer:
    return GroupLayer([points_layer, image_layer])


def test_qt_group_layer_model(group_layer_data: GroupLayer, qtmodeltester):
    model = QtGroupLayerModel(root=group_layer_data)
    qtmodeltester.check(model)
