from typing import Dict, Iterable, List

from napari.layers import Layer
from napari.utils.tree import Group


class GroupLayer(Group[Layer], Layer):
    def __init__(
        self, children: Iterable[Layer] = (), name: str = "grouped layers"
    ) -> None:
        def default_node_name():
            return "Node"

        for child in children:
            if not hasattr(
                child,
                "_node_name",
            ):
                child._node_name = default_node_name
        Group.__init__(self, children=children, name=name, basetype=Layer)
        group_emitters = self.events
        Layer.__init__(self, None, self._get_ndim(), name=name)
        self.events.add(**group_emitters.emitters)
        return

    def _extent_data(self):
        pass

    @property
    def ndim(self) -> int:
        return self._get_ndim()

    def _get_ndim(self) -> int:
        return max((c._get_ndim() for c in self), default=2)

    def _get_state(self) -> List[Dict]:
        state = [self._get_base_state()]
        if self is not None:
            state.extend(layer.get_state() for layer in self)
        return state

    def _get_value(self):
        pass

    def _set_view_slice(self):
        pass

    def _update_thumbnail(self):
        pass

    def data(self):
        pass
