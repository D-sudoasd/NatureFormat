"""Gating tests: shipped plan_layout for all 5 layouts × both column modes."""

from __future__ import annotations

import pytest

from natureformat.errors import PanelCountError, UnknownChoiceError
from natureformat.layouts import (
    COLUMN_DOUBLE,
    COLUMN_SINGLE,
    LAYOUT_NAMES,
    LAYOUT_SIX,
    PANEL_COUNT_BY_LAYOUT,
    grid_for,
    plan_layout,
)
from natureformat.spec import DOUBLE_COLUMN_WIDTH_MM, MAX_PAGE_HEIGHT_MM, SINGLE_COLUMN_WIDTH_MM


@pytest.mark.parametrize("layout", LAYOUT_NAMES)
@pytest.mark.parametrize("column", [COLUMN_SINGLE, COLUMN_DOUBLE])
def test_plan_layout_page_and_panels(column: str, layout: str) -> None:
    plan = plan_layout(column, layout)
    expected_width = (
        SINGLE_COLUMN_WIDTH_MM if column == COLUMN_SINGLE else DOUBLE_COLUMN_WIDTH_MM
    )
    expected_n = PANEL_COUNT_BY_LAYOUT[layout]
    assert plan.page_width_mm == expected_width
    assert plan.page_height_mm <= MAX_PAGE_HEIGHT_MM
    assert plan.panel_count == expected_n
    assert len(plan.panels) == expected_n
    labels = [box.label for box in plan.panels]
    assert labels == list("abcdefghi")[:expected_n]
    for box in plan.panels:
        assert box.x_mm >= 0
        assert box.y_mm >= 0
        assert box.width_mm > 0
        assert box.height_mm > 0
        assert box.right_mm() <= plan.page_width_mm + 1e-6
        assert box.bottom_mm() <= plan.page_height_mm + 1e-6


def test_six_grid_adapts_to_column_width() -> None:
    single = plan_layout(COLUMN_SINGLE, LAYOUT_SIX)
    double = plan_layout(COLUMN_DOUBLE, LAYOUT_SIX)
    assert grid_for(COLUMN_SINGLE, LAYOUT_SIX) == (3, 2)
    assert grid_for(COLUMN_DOUBLE, LAYOUT_SIX) == (2, 3)
    assert single.n_rows == 3 and single.n_cols == 2
    assert double.n_rows == 2 and double.n_cols == 3
    assert single.panel_count == double.panel_count == 6


def test_wrong_panel_count_is_error_not_silent_drop() -> None:
    with pytest.raises(PanelCountError, match="需要 6"):
        plan_layout(COLUMN_SINGLE, LAYOUT_SIX, panel_count=1)
    with pytest.raises(PanelCountError, match="需要 1"):
        plan_layout(COLUMN_DOUBLE, "单图（一行一图）", panel_count=9)
    with pytest.raises(PanelCountError, match="不会丢弃"):
        plan_layout(COLUMN_SINGLE, "两图一行", panel_count=3)


def test_unknown_layout_is_error() -> None:
    with pytest.raises(UnknownChoiceError, match="六宫格"):
        plan_layout(COLUMN_SINGLE, "四宫格")


def test_verbatim_layout_names() -> None:
    assert LAYOUT_NAMES == (
        "单图（一行一图）",
        "两图一行",
        "三图一行",
        "六宫格",
        "九宫格",
    )
    assert COLUMN_SINGLE == "单栏（Single Column）"
    assert COLUMN_DOUBLE == "双栏（Double Column）"
