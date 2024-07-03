from __future__ import annotations

import pytest
from qtpy.QtCore import Qt

# * imports into test files are considered bad, however
# importing fixtures defined in other files into conftest
# means we can avoid a large conftest.py file.
# It would be nice if ruff had an ignore block: https://github.com/astral-sh/ruff/issues/3711
from .fixtures.conftest_group_layers import *  # noqa: F403
from .fixtures.conftest_layers import *  # noqa: F403


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


@pytest.fixture
def right_click_on_view(qtbot):
    """Fixture to avoid code repetition to emulate right-click on a view."""

    def inner_right_click_on_view(view, index):
        viewport_index_position = view.visualRect(index).center()

        qtbot.mouseClick(
            view.viewport(),
            Qt.MouseButton.RightButton,
            pos=viewport_index_position,
        )

    return inner_right_click_on_view
