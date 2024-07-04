from __future__ import annotations

from typing import TYPE_CHECKING, List

from app_model.types import Action
from qtpy.QtCore import QPoint
from qtpy.QtWidgets import QAction, QMenu

from napari_experimental.group_layer import GroupLayer

if TYPE_CHECKING:
    from qtpy.QtWidgets import QWidget


class GroupLayerActions:
    """Class holding all GroupLayerActions to be shown in the right click
    context menu. Based on structure in napari/layers/_layer_actions and
    napari/app_model/actions/_layerlist_context_actions

    Parameters
    ----------
    group_layers: GroupLayer
        Group layers to apply actions to
    """

    def __init__(self, group_layers: GroupLayer) -> None:
        self.group_layers = group_layers

        self.actions: List[Action] = [
            Action(
                id="napari:grouplayer:toggle_visibility",
                title="toggle_visibility",
                callback=self._toggle_visibility,
            )
        ]

    def _toggle_visibility(self):
        """Toggle the visibility of all selected layers inside the
        group layers"""

        # Remove any selected items that are inside other selected groups
        # e.g. if a group is selected and also a layer inside it, toggling the
        # visibility will give odd results as toggling the group will toggle
        # the layer, then toggling the layer will toggle it again. We're
        # assuming groups higher up the tree have priority.
        items_to_toggle = self.group_layers.selection.copy()
        items_to_keep = []
        for sel_item in self.group_layers.selection:
            if sel_item.is_group():
                for item in items_to_toggle:
                    if item not in sel_item or item == sel_item:
                        items_to_keep.append(item)
                items_to_toggle = items_to_keep
                items_to_keep = []

        # Toggle the visibility of the relevant selection
        for item in items_to_toggle:
            if not item.is_group():
                visibility = item.layer.visible
                item.layer.visible = not visibility
            else:
                item.visible = not item.visible


class ContextMenu(QMenu):
    """Simplified context menu for the right click options. All actions are
    populated from GroupLayerActions.

    Parameters
    ----------
    group_layer_actions: GroupLayerActions
        Group layer actions used to populate actions in this menu
    title: str, optional
        Optional title for the menu
    parent: QWidget, optional
        Optional parent widget
    """

    def __init__(
        self,
        group_layer_actions: GroupLayerActions,
        title: str | None = None,
        parent: QWidget | None = None,
    ):
        QMenu.__init__(self, parent)
        self.group_layer_actions = group_layer_actions
        if title is not None:
            self.setTitle(title)
        self._populate_actions()

    def _populate_actions(self):
        """Populate menu actions from GroupLayerActions"""
        for gl_action in self.group_layer_actions.actions:
            action = QAction(gl_action.title, parent=self)
            action.triggered.connect(gl_action.callback)
            self.addAction(action)

    def exec_(self, pos: QPoint):
        """For now, rebuild actions every time the menu is shown. Otherwise,
        it doesn't react properly when items have been added/removed from
        the group_layer root"""
        self.clear()
        self._populate_actions()
        super().exec_(pos)
