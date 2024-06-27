"""Based on actions/_layer_actions.py and layers/_layer_actions.py in napari
"""

from __future__ import annotations

from typing import List

from app_model.types import Action
from napari._app_model.constants import MenuGroup

from napari_experimental.group_layer import GroupLayer

GROUP_LAYER_CONTEXT = "napari/grouplayers/context"


def _toggle_visibility(gl: GroupLayer):
    for item in gl.selection:
        if not item.is_group():
            visibility = item.layer.visible
            item.layer.visible = not visibility


GROUP_LAYER_ACTIONS: List[Action] = [
    Action(
        id="napari:grouplayer:toggle_visibility",
        title="toggle_visibility",
        callback=_toggle_visibility,
        menus=[
            {
                "id": GROUP_LAYER_CONTEXT,
                "group": MenuGroup.NAVIGATION,
            }
        ],
    )
]
