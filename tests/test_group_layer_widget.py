import pytest
from napari_experimental._widget import GroupLayerWidget
from napari_experimental.group_layer import GroupLayer, GroupLayerNode
from napari_experimental.group_layer_actions import GroupLayerActions
from napari_experimental.group_layer_delegate import GroupLayerDelegate
from qtpy.QtCore import QPoint, Qt
from qtpy.QtWidgets import QWidget


@pytest.fixture()
def group_layer_widget(make_napari_viewer, blobs):
    """Group layer widget with one image layer"""
    viewer = make_napari_viewer()
    viewer.add_image(blobs)
    return GroupLayerWidget(viewer)


@pytest.fixture()
def group_layer_widget_with_nested_groups(
    group_layer_widget, image_layer, points_layer
):
    """Group layer widget containing a group layer with images/points inside.
    The group layer (and all items inside of it) are selected. The group is
    visible, but not all of the items inside are."""
    group_layers = group_layer_widget.group_layers

    # Add a group layer with an image layer and point layer inside. One is
    # visible and the other is not
    group_layers.add_new_item()
    new_group = group_layers[1]

    image_layer.visible = True
    points_layer.visible = False
    new_group.add_new_item(layer_ptr=image_layer)
    new_group.add_new_item(layer_ptr=points_layer)
    new_image = new_group[0]
    new_points = new_group[1]

    # Select them all
    group_layers.propagate_selection(
        new_selection=[new_group, new_image, new_points]
    )

    return group_layer_widget


def test_widget_creation(make_napari_viewer) -> None:
    viewer = make_napari_viewer()
    assert isinstance(GroupLayerWidget(viewer), QWidget)


def test_rename_group_layer(group_layer_widget):
    group_layers_view = group_layer_widget.group_layers_view
    group_layers_model = group_layers_view.model()

    # Add an empty group layer
    group_layer_widget.group_layers.add_new_item()

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


def test_right_click_context_menu(
    group_layer_widget, right_click_on_view, mocker
):
    """Test that right clicking on an item in the view initiates the context
    menu"""

    # Using the real show_context_menu causes the test to hang, so mock it here
    mocker.patch.object(GroupLayerDelegate, "show_context_menu")

    group_layers_view = group_layer_widget.group_layers_view
    delegate = group_layers_view.itemDelegate()

    # right click on item and check show_context_menu is called
    node_index = group_layers_view.model().index(0, 0)
    right_click_on_view(group_layers_view, node_index)
    delegate.show_context_menu.assert_called_once()


def test_actions_context_menu(
    group_layer_widget, right_click_on_view, monkeypatch
):
    """Test that the context menu contains the correct actions"""

    group_layers_view = group_layer_widget.group_layers_view
    delegate = group_layers_view.itemDelegate()
    assert not hasattr(delegate, "_context_menu")

    # Uses same setup as inside napari's test_qt_layer_list (otherwise the
    # context menu hangs in the test)
    monkeypatch.setattr(
        "napari_experimental.group_layer_actions.ContextMenu.exec_",
        lambda self, x: x,
    )

    # Show the context menu directly
    node_index = group_layers_view.model().index(0, 0)
    delegate.show_context_menu(
        node_index,
        group_layers_view.model(),
        QPoint(10, 10),
        parent=group_layers_view,
    )
    assert hasattr(delegate, "_context_menu")

    # Test number and name of actions in the context menu matches
    # GroupLayerActions
    assert len(delegate._context_menu.actions()) == len(
        delegate._group_layer_actions.actions
    )
    context_menu_action_names = [
        action.text() for action in delegate._context_menu.actions()
    ]
    group_layer_action_names = [
        action.title for action in delegate._group_layer_actions.actions
    ]
    assert context_menu_action_names == group_layer_action_names


def test_toggle_visibility_layer_via_context_menu(group_layer_widget):
    group_layers = group_layer_widget.group_layers
    group_layer_actions = GroupLayerActions(group_layers)

    assert group_layers[0].layer.visible is True
    group_layer_actions._toggle_visibility()
    assert group_layers[0].layer.visible is False


def test_toggle_visibility_layer_via_model(group_layer_widget):
    group_layers = group_layer_widget.group_layers
    group_layers_view = group_layer_widget.group_layers_view
    group_layers_model = group_layers_view.model()

    assert group_layers[0].layer.visible is True

    node_index = group_layers_model.index(0, 0)
    group_layers_model.setData(
        node_index,
        Qt.CheckState.Unchecked,
        role=Qt.ItemDataRole.CheckStateRole,
    )

    assert group_layers[0].layer.visible is False


def test_toggle_visibility_group_layer_via_context_menu(
    group_layer_widget_with_nested_groups,
):
    group_layers = group_layer_widget_with_nested_groups.group_layers
    group_layer_actions = GroupLayerActions(group_layers)

    # Check starting visibility of group layer and items inside
    new_group = group_layers[1]
    new_image = new_group[0]
    new_points = new_group[1]
    assert new_group.visible is True
    assert new_image.layer.visible is True
    assert new_points.layer.visible is False

    # Toggle visibility and check all become False. As both the image and point
    # are inside the new_group, the group takes priority.
    group_layer_actions._toggle_visibility()
    assert new_group.visible is False
    assert new_image.layer.visible is False
    assert new_points.layer.visible is False


def test_toggle_visibility_group_layer_via_model(
    group_layer_widget_with_nested_groups,
):
    group_layers = group_layer_widget_with_nested_groups.group_layers
    group_layers_model = (
        group_layer_widget_with_nested_groups.group_layers_view.model()
    )

    # Check starting visibility of group layer and items inside
    new_group = group_layers[1]
    new_image = new_group[0]
    new_points = new_group[1]
    assert new_group.visible is True
    assert new_image.layer.visible is True
    assert new_points.layer.visible is False

    # Toggle visibility and check all become False. As both the image and point
    # are inside the new_group, the group takes priority.
    node_index = group_layers_model.nestedIndex(new_group.index_from_root())
    group_layers_model.setData(
        node_index,
        Qt.CheckState.Unchecked,
        role=Qt.ItemDataRole.CheckStateRole,
    )
    assert new_group.visible is False
    assert new_image.layer.visible is False
    assert new_points.layer.visible is False
