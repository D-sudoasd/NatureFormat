"""UI and CLI share the verbatim column/layout names."""

from __future__ import annotations

from natureformat.layouts import COLUMN_CHOICES, COLUMN_DOUBLE, COLUMN_SINGLE, LAYOUT_NAMES
from natureformat.ui import LAYOUT_CHOICES, restyle_path


def test_ui_names_match_requested_copy() -> None:
    assert COLUMN_CHOICES == (
        "单栏（Single Column）",
        "双栏（Double Column）",
    )
    assert LAYOUT_CHOICES == (
        "单图（一行一图）",
        "两图一行",
        "三图一行",
        "六宫格",
        "九宫格",
    )
    assert LAYOUT_CHOICES is LAYOUT_NAMES or tuple(LAYOUT_CHOICES) == LAYOUT_NAMES
    assert COLUMN_SINGLE in COLUMN_CHOICES
    assert COLUMN_DOUBLE in COLUMN_CHOICES


def test_ui_restyle_path_is_the_shipped_apply() -> None:
    assert restyle_path.__module__ == "natureformat.ui"
    assert restyle_path.__name__ == "restyle_path"
