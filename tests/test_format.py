"""Gating tests: shipped apply_nature_format on an already-assembled figure."""

from __future__ import annotations

from pathlib import Path

import pytest

from natureformat.apply import apply_nature_format
from natureformat.demo import assembled_figure
from natureformat.errors import NatureSpecError, PanelCountError
from natureformat.figure import load_figure
from natureformat.layouts import COLUMN_DOUBLE, COLUMN_SINGLE
from natureformat.spec import (
    FONT_ARIAL,
    FONT_HELVETICA,
    NATURE_FONTS,
    PANEL_LABEL_PT,
    PANEL_LABEL_STYLE,
    PANEL_LABEL_WEIGHT,
    STROKE_PT_MAX,
    STROKE_PT_MIN,
    TEXT_SIZE_PT_MAX,
    TEXT_SIZE_PT_MIN,
)

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "assembled_six_panel.json"


def _assert_nature_text(style, *, panel_label: bool = False) -> None:
    assert style.family in NATURE_FONTS
    if panel_label:
        assert style.size_pt == PANEL_LABEL_PT
        assert style.weight == PANEL_LABEL_WEIGHT
        assert style.style == PANEL_LABEL_STYLE
    else:
        assert TEXT_SIZE_PT_MIN <= style.size_pt <= TEXT_SIZE_PT_MAX


def test_apply_preserves_data_markers_colors_and_sets_nature_style() -> None:
    figure = load_figure(EXAMPLE)
    before = figure.plot_identity()
    assert any(item[2] == "circle" for item in before)
    assert any(item[2] == "square" for item in before)
    colors = {item[3] for item in before}
    assert "#D62728" in colors and "#1F77B4" in colors

    result = apply_nature_format(figure, COLUMN_SINGLE, "六宫格")
    styled = result.figure
    assert styled.plot_identity() == before
    assert result.plan.page_width_mm == 89.0
    assert result.plan.panel_count == 6

    for panel, box in zip(styled.panels, result.plan.panels, strict=True):
        _assert_nature_text(panel.title_font)
        assert panel.panel_label == box.label
        assert panel.panel_label_font is not None
        _assert_nature_text(panel.panel_label_font, panel_label=True)
        for note in panel.annotations:
            _assert_nature_text(note.font)
            assert note.text == "note"
        for axis in (panel.x_axis, panel.y_axis):
            _assert_nature_text(axis.tick_font)
            _assert_nature_text(axis.title_font)
            assert STROKE_PT_MIN <= axis.line_weight_pt <= STROKE_PT_MAX
            assert STROKE_PT_MIN <= axis.tick_weight_pt <= STROKE_PT_MAX
        assert panel.width_mm == box.width_mm
        assert panel.height_mm == box.height_mm


def test_axis_body_and_tick_numbers_are_independent() -> None:
    figure = assembled_figure(2)
    thin = apply_nature_format(
        figure,
        COLUMN_DOUBLE,
        "两图一行",
        axis_line_pt=0.25,
        tick_label_pt=5.0,
    )
    thick = apply_nature_format(
        figure,
        COLUMN_DOUBLE,
        "两图一行",
        axis_line_pt=1.0,
        tick_label_pt=7.0,
    )
    a0 = thin.figure.panels[0].x_axis
    b0 = thick.figure.panels[0].x_axis
    assert a0.line_weight_pt != b0.line_weight_pt
    assert a0.tick_font.size_pt != b0.tick_font.size_pt
    assert a0.line_weight_pt == 0.25
    assert b0.line_weight_pt == 1.0
    assert a0.tick_font.size_pt == 5.0
    assert b0.tick_font.size_pt == 7.0
    assert thin.figure.plot_identity() == figure.plot_identity()
    assert thick.figure.plot_identity() == figure.plot_identity()


def test_helvetica_allowed_and_source_figure_not_mutated() -> None:
    figure = assembled_figure(1)
    original_family = figure.panels[0].title_font.family
    result = apply_nature_format(
        figure,
        COLUMN_SINGLE,
        "单图（一行一图）",
        font_family=FONT_HELVETICA,
    )
    assert result.figure.panels[0].title_font.family == FONT_HELVETICA
    assert figure.panels[0].title_font.family == original_family
    assert result.figure.panels[0].panel_label is None


def test_wrong_panel_count_on_apply() -> None:
    figure = assembled_figure(3)
    with pytest.raises(PanelCountError, match="需要 6"):
        apply_nature_format(figure, COLUMN_SINGLE, "六宫格")


def test_out_of_range_axis_or_font_is_error() -> None:
    figure = assembled_figure(1)
    with pytest.raises(NatureSpecError, match="轴体"):
        apply_nature_format(figure, COLUMN_SINGLE, "单图（一行一图）", axis_line_pt=2.0)
    with pytest.raises(NatureSpecError, match="轴上数字"):
        apply_nature_format(figure, COLUMN_SINGLE, "单图（一行一图）", tick_label_pt=12.0)
    with pytest.raises(NatureSpecError, match="Arial"):
        apply_nature_format(figure, COLUMN_SINGLE, "单图（一行一图）", font_family="Times New Roman")


def test_ui_restyle_path_uses_shipped_apply() -> None:
    from natureformat.ui import restyle_path

    result = restyle_path(EXAMPLE, COLUMN_SINGLE, "六宫格", axis_line_pt=0.5, tick_label_pt=6.0)
    assert result.plan.page_width_mm == 89.0
    assert result.figure.plot_identity() == load_figure(EXAMPLE).plot_identity()
    assert result.figure.panels[0].title_font.family == FONT_ARIAL
