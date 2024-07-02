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


def test_layer_sync(make_napari_viewer, image_layer, points_layer):
    """
    Test the synchronisation between the widget and the main LayerList.
    This test will be redundant when the plugin functionality replaces the
    main viewer functionality.
    """
    viewer = make_napari_viewer()
    viewer.add_layer(image_layer)

    widget = GroupLayerWidget(viewer)
    assert len(widget.group_layers) == 1

    # Check that adding a layer to the viewer means it is also added to
    # the group layers view.

    viewer.add_layer(points_layer)
    assert len(widget.group_layers) == 2

    # Check that reordering the layer order in the group layers view
    # forces an update in the main viewer.
    # However, don't forget that the ordering is REVERSED in the GUI, so
    # viewer.layers[-1] == widget.group_layers[0], etc.
    for in_viewer, in_widget in zip(
        reversed(viewer.layers),
        [node.layer for node in widget.group_layers],
        strict=True,
    ):
        assert in_viewer is in_widget
    # Move layer at position 1 to position 0
    widget.group_layers.move((1,), (0,))
    # Viewer should have auto-synced these changes
    for in_viewer, in_widget in zip(
        reversed(viewer.layers),
        [node.layer for node in widget.group_layers],
        strict=True,
    ):
        assert in_viewer is in_widget

    # Deletion in main viewer results in deletion in group layers viewer
    viewer.layers.remove(points_layer)
    assert len(widget.group_layers) == 1
    assert image_layer is widget.group_layers[0].layer
    # Deletion in group layers viewer results in deletion in main viewer
    widget.group_layers.remove_layer_item(image_layer)
    assert len(viewer.layers) == 0
