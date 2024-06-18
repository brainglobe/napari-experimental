from napari_experimental._widget import GroupLayerWidget
from qtpy.QtWidgets import QWidget


def test_me() -> None:
    assert isinstance(GroupLayerWidget, QWidget)
