from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING, Optional, Tuple

from app_model.expressions import ContextKey
from napari._app_model.context import LayerListContextKeys
from napari.utils._dtype import normalize_dtype
from napari.utils.translations import trans

if TYPE_CHECKING:
    from napari.utils.events import Selection
    from numpy.typing import DTypeLike

    from napari_experimental.group_layer import GroupLayer

    LayerSel = Selection[GroupLayer]


def _len(s: LayerSel) -> int:
    return len(s)


def _all_linked(s: LayerSel) -> bool:
    from napari.layers.utils._link_layers import layer_is_linked

    return bool(
        s and all(layer_is_linked(x.layer) for x in s if not x.is_group())
    )


def _n_unselected_links(s: LayerSel) -> int:
    from napari.layers.utils._link_layers import get_linked_layers

    return len(get_linked_layers(*s) - s)


def _is_rgb(s: LayerSel) -> bool:
    if s.active and not s.active.is_group():
        return getattr(s.active.layer, "rgb", False)
    else:
        return False


def _only_img(s: LayerSel) -> bool:
    return bool(
        s
        and all(x.layer._type_string == "image" for x in s if not x.is_group())
    )


def _n_selected_imgs(s: LayerSel) -> int:
    return sum(x.layer._type_string == "image" for x in s if not x.is_group())


def _only_labels(s: LayerSel) -> bool:
    return bool(
        s
        and all(
            x.layer._type_string == "labels" for x in s if not x.is_group()
        )
    )


def _n_selected_labels(s: LayerSel) -> int:
    return sum(x.layer._type_string == "labels" for x in s if not x.is_group())


def _only_points(s: LayerSel) -> bool:
    return bool(
        s
        and all(
            x.layer._type_string == "points" for x in s if not x.is_group()
        )
    )


def _n_selected_points(s: LayerSel) -> int:
    return sum(x.layer._type_string == "points" for x in s if not x.is_group())


def _only_shapes(s: LayerSel) -> bool:
    return bool(
        s
        and all(
            x.layer._type_string == "shapes" for x in s if not x.is_group()
        )
    )


def _n_selected_shapes(s: LayerSel) -> int:
    return sum(x.layer._type_string == "shapes" for x in s if not x.is_group())


def _only_surface(s: LayerSel) -> bool:
    return bool(
        s
        and all(
            x.layer._type_string == "surface" for x in s if not x.is_group()
        )
    )


def _n_selected_surfaces(s: LayerSel) -> int:
    return sum(
        x.layer._type_string == "surface" for x in s if not x.is_group()
    )


def _only_vectors(s: LayerSel) -> bool:
    return bool(
        s
        and all(
            x.layer._type_string == "vectors" for x in s if not x.is_group()
        )
    )


def _n_selected_vectors(s: LayerSel) -> int:
    return sum(
        x.layer._type_string == "vectors" for x in s if not x.is_group()
    )


def _only_tracks(s: LayerSel) -> bool:
    return bool(
        s
        and all(
            x.layer._type_string == "tracks" for x in s if not x.is_group()
        )
    )


def _n_selected_tracks(s: LayerSel) -> int:
    return sum(x.layer._type_string == "tracks" for x in s if not x.is_group())


def _active_type(s: LayerSel) -> Optional[str]:
    if s.active and not s.active.is_group():
        return s.active.layer._type_string
    else:
        return None
    # return s.active._type_string if s.active else None


def _active_ndim(s: LayerSel) -> Optional[int]:
    if s.active and not s.active.is_group():
        return getattr(s.active.layer.data, "ndim", None)
    else:
        return None

    # return getattr(s.active.data, "ndim", None) if s.active else None


def _active_shape(s: LayerSel) -> Optional[Tuple[int, ...]]:
    if s.active and not s.active.is_group():
        return getattr(s.active.layer.data, "shape", None)
    else:
        return None


def _same_shape(s: LayerSel) -> bool:
    return (
        len(
            {getattr(x.layer.data, "shape", ()) for x in s if not x.is_group()}
        )
        == 1
    )


def _active_dtype(s: LayerSel) -> DTypeLike:
    dtype = None
    if s.active and not s.active.is_group():
        with contextlib.suppress(AttributeError):
            dtype = normalize_dtype(s.active.layer.data.dtype).__name__
    return dtype


def _same_type(s: LayerSel) -> bool:
    return len({x.layer._type_string for x in s if not x.is_group()}) == 1


def _active_is_image_3d(s: LayerSel) -> bool:
    return (
        _active_type(s) == "image"
        and _active_ndim(s) is not None
        and (_active_ndim(s) > 3 or (_active_ndim(s) > 2 and not _is_rgb(s)))
    )


def _empty_shapes_layer_selected(s: LayerSel) -> bool:
    return any(
        x.layer._type_string == "shapes" and not len(x.layer.data)
        for x in s
        if not x.is_group()
    )


class GroupLayerContextKeys(LayerListContextKeys):

    num_selected_layers = ContextKey(
        0,
        trans._("Number of currently selected layers."),
        _len,
    )
    num_selected_layers_linked = ContextKey(
        False,
        trans._("True when all selected layers are linked."),
        _all_linked,
    )
    num_unselected_linked_layers = ContextKey(
        0,
        trans._("Number of unselected layers linked to selected layer(s)."),
        _n_unselected_links,
    )
    active_layer_is_rgb = ContextKey(
        False,
        trans._("True when the active layer is RGB."),
        _is_rgb,
    )
    active_layer_type = ContextKey["LayerSel", Optional[str]](
        None,
        trans._(
            "Lowercase name of active layer type, or None of none active."
        ),
        _active_type,
    )

    num_selected_image_layers = ContextKey(
        0,
        trans._("Number of selected image layers."),
        _n_selected_imgs,
    )
    num_selected_labels_layers = ContextKey(
        0,
        trans._("Number of selected labels layers."),
        _n_selected_labels,
    )
    num_selected_points_layers = ContextKey(
        0,
        trans._("Number of selected points layers."),
        _n_selected_points,
    )
    num_selected_shapes_layers = ContextKey(
        0,
        trans._("Number of selected shapes layers."),
        _n_selected_shapes,
    )
    num_selected_surface_layers = ContextKey(
        0,
        trans._("Number of selected surface layers."),
        _n_selected_surfaces,
    )
    num_selected_vectors_layers = ContextKey(
        0,
        trans._("Number of selected vectors layers."),
        _n_selected_vectors,
    )
    num_selected_tracks_layers = ContextKey(
        0,
        trans._("Number of selected tracks layers."),
        _n_selected_tracks,
    )
    active_layer_ndim = ContextKey["LayerSel", Optional[int]](
        None,
        trans._(
            "Number of dimensions in the active layer, or `None` if nothing "
            "is active."
        ),
        _active_ndim,
    )
    active_layer_shape = ContextKey["LayerSel", Optional[Tuple[int, ...]]](
        (),
        trans._("Shape of the active layer, or `None` if nothing is active."),
        _active_shape,
    )
    active_layer_is_image_3d = ContextKey(
        False,
        trans._("True when the active layer is a 3D image."),
        _active_is_image_3d,
    )
    active_layer_dtype = ContextKey(
        None,
        trans._("Dtype of the active layer, or `None` if nothing is active."),
        _active_dtype,
    )
    all_selected_layers_same_shape = ContextKey(
        False,
        trans._("True when all selected layers have the same shape."),
        _same_shape,
    )
    all_selected_layers_same_type = ContextKey(
        False,
        trans._("True when all selected layers are of the same type."),
        _same_type,
    )
    all_selected_layers_labels = ContextKey(
        False,
        trans._("True when all selected layers are labels."),
        _only_labels,
    )
    selected_empty_shapes_layer = ContextKey(
        False,
        trans._("True when there is a shapes layer without data selected."),
        _empty_shapes_layer_selected,
    )
