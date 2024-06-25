from napari._qt.layer_controls.qt_image_controls import QtImageControls
from napari._qt.layer_controls.qt_points_controls import QtPointsControls
from napari.layers import Image, Points
from napari_experimental.group_layer_controls import (
    QtGroupLayerControls,
    QtGroupLayerControlsContainer,
)


def test_controls_selection(make_napari_viewer, group_layer_data):
    """Test that group layer controls initialise with the correct widget, and
    match changes to the selected item."""
    viewer = make_napari_viewer()
    # Add an empty group also
    group_layer_data.add_new_item()

    # Initialise with image item selected
    image_item = group_layer_data[1]
    assert isinstance(image_item.layer, Image)
    group_layer_data.selection.active = image_item

    controls = QtGroupLayerControlsContainer(viewer, group_layer_data)
    assert isinstance(
        controls.currentWidget(), QtImageControls
    ), "Initial widget doesn't match selected image layer"

    # Switch to points item selected
    points_item = group_layer_data[0]
    assert isinstance(points_item.layer, Points)
    group_layer_data.selection.active = points_item
    assert isinstance(
        controls.currentWidget(), QtPointsControls
    ), "Current widget doesn't match selected points layer"

    # Switch to group layer selected
    group_item = group_layer_data[-1]
    assert group_layer_data.is_group()
    group_layer_data.selection.active = group_item
    assert isinstance(
        controls.currentWidget(), QtGroupLayerControls
    ), "Current widget doesn't match selected group layer"


def test_controls_insertion(make_napari_viewer, group_layer_data, blobs):
    """Test that insertions into group layers are reflected in the controls
    widgets"""
    viewer = make_napari_viewer()
    controls = QtGroupLayerControlsContainer(viewer, group_layer_data)

    # Every item in group layer data should have a corresponding widget
    n_items = len(group_layer_data)
    assert len(controls.widgets) == n_items
    for item in group_layer_data:
        assert item in controls.widgets

    new_layer = Image(
        blobs, scale=(1, 2), translate=(20, 15), name="new-blobs"
    )
    group_layer_data.add_new_item(layer_ptr=new_layer)

    # Check that adding an item to group layers, also appears in the widgets
    assert len(group_layer_data) == n_items + 1
    assert len(controls.widgets) == n_items + 1
    assert group_layer_data[-1] in controls.widgets


def test_controls_deletion(make_napari_viewer, group_layer_data):
    """Test that deletion from group layers is reflected in the controls
    widgets"""
    viewer = make_napari_viewer()
    controls = QtGroupLayerControlsContainer(viewer, group_layer_data)

    # Every item in group layer data should have a corresponding widget
    n_items = len(group_layer_data)
    assert len(controls.widgets) == n_items
    for item in group_layer_data:
        assert item in controls.widgets

    item_to_remove = group_layer_data[0]
    group_layer_data.remove_layer_item(layer_ptr=item_to_remove.layer)

    # Check that removing an item from group layers, is reflected in
    # the widgets
    assert len(group_layer_data) == n_items - 1
    assert len(controls.widgets) == n_items - 1
    assert item_to_remove not in controls.widgets
