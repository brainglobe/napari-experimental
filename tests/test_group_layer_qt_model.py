from napari_experimental.group_layer import GroupLayer
from napari_experimental.group_layer_qt import QtGroupLayerModel


def test_qt_group_layer_model(
    group_layer_data: GroupLayer, nested_group_data: GroupLayer, qtmodeltester
) -> None:
    simple = QtGroupLayerModel(root=group_layer_data)
    qtmodeltester.check(simple)

    nested = QtGroupLayerModel(nested_group_data)
    qtmodeltester.check(nested)
