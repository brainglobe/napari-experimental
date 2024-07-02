from __future__ import annotations

from typing import TYPE_CHECKING

from app_model.expressions import ContextKey
from napari._app_model.context import LayerListContextKeys
from napari.utils.translations import trans

if TYPE_CHECKING:
    from napari.utils.events import Selection

    from napari_experimental.group_layer import GroupLayer

    LayerSel = Selection[GroupLayer]


def _len(s: LayerSel) -> int:
    return len(s)


class GroupLayerContextKeys(LayerListContextKeys):
    """These are the available context keys relating to GroupLayers.
    Currently only num_selected_layers is overriden, but more methods from
    LayerListContextKeys could be added to provide further context.
    """

    num_selected_layers = ContextKey(
        0,
        trans._("Number of currently selected layers."),
        _len,
    )
