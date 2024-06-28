import pytest
from napari_experimental._widget import GroupLayerWidget
from napari_experimental.group_layer import GroupLayer, GroupLayerNode
from qtpy.QtWidgets import QWidget


@pytest.fixture()
def group_layer_widget(make_napari_viewer, blobs) -> GroupLayerWidget:
    viewer = make_napari_viewer()
    viewer.add_image(blobs)
    return GroupLayerWidget(viewer)


def test_widget_creation(make_napari_viewer_proxy) -> None:
    viewer = make_napari_viewer_proxy()
    assert isinstance(GroupLayerWidget(viewer), QWidget)


def test_rename_group_layer(group_layer_widget: GroupLayerWidget):
    group_layers_view = group_layer_widget.group_layers_view
    group_layers_model = group_layers_view.model()

    # Add an empty group layer
    group_layer_widget.group_layers.add_new_group()

    # Check current name
    new_name = "renamed-group"
    node_index = group_layers_model.index(group_layers_model.rowCount(), 0)
    group_layer = group_layers_model.getItem(node_index)
    assert isinstance(group_layer, GroupLayer)
    assert group_layer.name != new_name

    # Rename
    group_layers_model.setData(node_index, new_name)
    assert group_layers_model.getItem(node_index).name == new_name
    assert (
        group_layers_model.getItem(node_index)._node_name() == f"GL-{new_name}"
    )


def test_rename_layer(group_layer_widget):
    group_layers_view = group_layer_widget.group_layers_view
    group_layers_model = group_layers_view.model()

    # Check current name
    node_index = group_layers_model.index(0, 0)
    node = group_layers_model.getItem(node_index)
    assert isinstance(node, GroupLayerNode)
    assert node.name == "blobs"

    # Rename
    new_name = "new-blobs"
    group_layers_model.setData(node_index, new_name)
    assert group_layers_model.getItem(node_index).name == new_name
    assert group_layers_model.getItem(node_index)._node_name() == new_name


def test_double_click_edit(group_layer_widget, double_click_on_view):
    """Check that the view enters editing state when an item is
    double-clicked"""
    group_layers_view = group_layer_widget.group_layers_view
    group_layers_model = group_layers_view.model()
    assert group_layers_view.state() == group_layers_view.NoState

    # Check enters editing state on double click
    node_index = group_layers_model.index(0, 0)
    double_click_on_view(group_layers_view, node_index)
    assert group_layers_view.state() == group_layers_view.EditingState
