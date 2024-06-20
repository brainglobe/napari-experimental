from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import pytest
from napari.layers import Image, Points
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
