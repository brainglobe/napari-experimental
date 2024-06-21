from napari_experimental.group_layer import GroupLayer
from napari_experimental.group_layer_qt import QtGroupLayerModel


def test_qt_group_layer_model(
    group_layer_data: GroupLayer, nested_layer_group: GroupLayer, qtmodeltester
) -> None:
    simple = QtGroupLayerModel(root=group_layer_data)
    qtmodeltester.check(simple)

    nested = QtGroupLayerModel(nested_layer_group)
    qtmodeltester.check(nested)
