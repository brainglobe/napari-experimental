from napari_experimental._widget import GroupLayerWidget
from qtpy.QtWidgets import QWidget


def test_widget_creation(make_napari_viewer_proxy) -> None:
    viewer = make_napari_viewer_proxy()
    assert isinstance(GroupLayerWidget(viewer), QWidget)
