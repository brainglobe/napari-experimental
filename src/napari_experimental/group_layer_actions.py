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


# def _add_to_new_group(gl: GroupLayer):
#     selected_items = gl.selection
#     # selected_items = gl.all_selected_items()
#     selected_items = [item for item in selected_items if not item.is_group()]
#     if len(selected_items) > 0:
#         for i, item in enumerate(selected_items):
#             gl.remove_layer_item(layer_ptr=item.layer)
#             if i == 0:
#                 gl.add_new_item()
#                 new_group = gl[-1]
#             new_group.add_new_item(layer_ptr=item.layer)
#
#     gl.selection.select_only(new_group)


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
    ),
    # Action(
    #     id="napari:grouplayer:add_to_new_group",
    #     title="add_to_new_group",
    #     callback=_add_to_new_group,
    #     menus=[
    #         {
    #             "id": GROUP_LAYER_CONTEXT,
    #             "group": MenuGroup.NAVIGATION,
    #         }
    #     ],
    # )
]
