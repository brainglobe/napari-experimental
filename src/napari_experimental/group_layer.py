from __future__ import annotations

from typing import TypeAlias

from napari.layers.base import Layer

# from napari.utils.tree import Group

GroupableTypes: TypeAlias = Layer | "GroupLayer"


class GroupLayer:
    pass
