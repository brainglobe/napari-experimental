from __future__ import annotations

from copy import deepcopy
from typing import TYPE_CHECKING, Any, Dict

import numpy as np
import pytest
from napari.layers import Image, Points
from skimage import data

if TYPE_CHECKING:
    import numpy.typing as npt


SEED = 0
GENERATOR = np.random.RandomState(seed=SEED)


def return_copy_with_new_name(obj: Any, new_name: str = "Copy") -> Any:
    """
    Returns a copy of the object that is passed with the name
    attribute set to the new name provided.
    If an object does not have a name attribute, this method
    will add one to the returned copy.
    """
    copy = deepcopy(obj)
    copy.name = new_name
    return copy


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


@pytest.fixture(scope="function")
def collection_of_layers(points_layer) -> Dict[str, Points]:
    """
    Creates a Dictionary containing with key (str) : value (Points)
    items that can be used to instantiate other objects if necessary.

    Objects persist in memory until end of test so that use of the IS
    comparison is correctly carried out.

    For a given key k, the Points layer value has the name Points_{k}.
    Otherwise, all Points layers are identical.
    Valid keys (all strings):
    - 0
    - A0
    - A1
    - AA0
    - AA1
    - 1
    - B0
    """
    return {
        key: return_copy_with_new_name(points_layer, f"Points_{key}")
        for key in ["0", "A0", "A1", "AA0", "AA1", "1", "B0"]
    }


@pytest.fixture(scope="function")
def n_layers_in_collection(collection_of_layers: Dict[str, Points]) -> int:
    return len(collection_of_layers)
