from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import pytest
from napari.layers import Image, Points
from qtpy.QtCore import Qt
from skimage import data

if TYPE_CHECKING:
    import numpy.typing as npt

SEED = 0
GENERATOR = np.random.RandomState(seed=SEED)


@pytest.fixture(scope="session")
def blobs() -> npt.NDArray:
    return data.binary_blobs(length=100, volume_fraction=0.05, n_dim=2)


@pytest.fixture(scope="function")
def image_layer(blobs) -> Image:
    return Image(blobs, scale=(1, 2), translate=(20, 15))


@pytest.fixture(scope="session")
def points() -> npt.NDArray:
    return GENERATOR.rand(10, 3) * (1, 2, 3) * 100


@pytest.fixture(scope="session")
def colors() -> npt.NDArray:
    return GENERATOR.rand(10, 3)


@pytest.fixture(scope="function")
def points_layer(points, colors) -> Points:
    return Points(points, face_color=colors)


@pytest.fixture
def double_click_on_view(qtbot):
    """Fixture to avoid code repetition to emulate double-click on a view."""

    def inner_double_click_on_view(view, index):
        viewport_index_position = view.visualRect(index).center()

        # weirdly, to correctly emulate a double-click
        # you need to click first. Also, note that the view
        # needs to be interacted with via its viewport
        qtbot.mouseClick(
            view.viewport(),
            Qt.MouseButton.LeftButton,
            pos=viewport_index_position,
        )
        qtbot.mouseDClick(
            view.viewport(),
            Qt.MouseButton.LeftButton,
            pos=viewport_index_position,
        )

    return inner_double_click_on_view
