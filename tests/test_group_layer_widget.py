import pytest
from napari_experimental._widget import GroupLayerWidget
from napari_experimental.group_layer import GroupLayer, GroupLayerNode
from napari_experimental.group_layer_delegate import GroupLayerDelegate
from qtpy.QtCore import QPoint
from qtpy.QtWidgets import QWidget


@pytest.fixture()
def group_layer_widget(make_napari_viewer, blobs):
    viewer = make_napari_viewer()
    viewer.add_image(blobs)

    _, plugin_widget = viewer.window.add_plugin_dock_widget(
        "napari-experimental", "Show Grouped Layers"
    )
    return plugin_widget


def test_widget_creation(make_napari_viewer_proxy) -> None:
    viewer = make_napari_viewer_proxy()
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
