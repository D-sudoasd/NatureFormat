"""Format-apply: Nature typography and axis weights; never touch data/markers/colors."""

from __future__ import annotations

from dataclasses import dataclass

from .errors import NatureSpecError, PanelCountError
from .figure import Figure, TextStyle
from .layouts import LayoutPlan, plan_layout
from .spec import (
    DEFAULT_ANNOTATION_PT,
    DEFAULT_AXIS_LINE_PT,
    DEFAULT_AXIS_TITLE_PT,
    DEFAULT_TICK_LABEL_PT,
    DEFAULT_TICK_LINE_PT,
    DEFAULT_TITLE_PT,
    FONT_ARIAL,
    NATURE_FONTS,
    PANEL_LABEL_PT,
    PANEL_LABEL_STYLE,
    PANEL_LABEL_WEIGHT,
    STROKE_PT_MAX,
    STROKE_PT_MIN,
    TEXT_SIZE_PT_MAX,
    TEXT_SIZE_PT_MIN,
)


def _in_text_window(size_pt: float) -> bool:
    return TEXT_SIZE_PT_MIN - 1e-9 <= float(size_pt) <= TEXT_SIZE_PT_MAX + 1e-9


def _in_stroke_window(size_pt: float) -> bool:
    return STROKE_PT_MIN - 1e-9 <= float(size_pt) <= STROKE_PT_MAX + 1e-9


def _check_font_family(font_family: str) -> str:
    if font_family not in NATURE_FONTS:
        raise NatureSpecError(
            f"字体必须是 Arial 或 Helvetica，收到：{font_family!r}"
        )
    return font_family


def _check_text_pt(name: str, size_pt: float) -> float:
    value = float(size_pt)
    if not _in_text_window(value):
        raise NatureSpecError(
            f"{name} 必须在 {TEXT_SIZE_PT_MIN:g}–{TEXT_SIZE_PT_MAX:g} pt，收到：{size_pt}"
        )
    return value


def _check_stroke_pt(name: str, size_pt: float) -> float:
    value = float(size_pt)
    if not _in_stroke_window(value):
        raise NatureSpecError(
            f"{name} 必须在 {STROKE_PT_MIN:g}–{STROKE_PT_MAX:g} pt，收到：{size_pt}"
        )
    return value


def _text(family: str, size_pt: float, *, weight: str = "normal", style: str = "normal") -> TextStyle:
    return TextStyle(family=family, size_pt=size_pt, weight=weight, style=style)


@dataclass(frozen=True)
class RestyleResult:
    figure: Figure
    plan: LayoutPlan
    font_family: str
    title_pt: float
    annotation_pt: float
    tick_label_pt: float
    axis_title_pt: float
    axis_line_pt: float
    tick_line_pt: float


def apply_nature_format(
    figure: Figure,
    column_mode: str,
    layout_name: str,
    *,
    font_family: str = FONT_ARIAL,
    title_pt: float = DEFAULT_TITLE_PT,
    annotation_pt: float = DEFAULT_ANNOTATION_PT,
    tick_label_pt: float = DEFAULT_TICK_LABEL_PT,
    axis_title_pt: float = DEFAULT_AXIS_TITLE_PT,
    axis_line_pt: float = DEFAULT_AXIS_LINE_PT,
    tick_line_pt: float | None = None,
) -> RestyleResult:
    """Restyle an already-assembled figure.

    Changes page size, panel boxes, 标题 / 图内注释 / 坐标轴数字 fonts,
    轴体 and tick line weights. Leaves series x/y, marker shapes, and colors
    byte-for-byte as they were.
    """
    family = _check_font_family(font_family)
    title_pt = _check_text_pt("标题字号", title_pt)
    annotation_pt = _check_text_pt("图内注释字号", annotation_pt)
    tick_label_pt = _check_text_pt("轴上数字字号", tick_label_pt)
    axis_title_pt = _check_text_pt("轴标题字号", axis_title_pt)
    axis_line_pt = _check_stroke_pt("轴体线宽", axis_line_pt)
    tick_width = DEFAULT_TICK_LINE_PT if tick_line_pt is None else float(tick_line_pt)
    tick_width = _check_stroke_pt("刻度线宽", tick_width)

    plan = plan_layout(column_mode, layout_name, panel_count=len(figure.panels))
    styled = figure.copy()
    styled.width_mm = plan.page_width_mm
    styled.height_mm = plan.page_height_mm

    title_font = _text(family, title_pt)
    annotation_font = _text(family, annotation_pt)
    tick_font = _text(family, tick_label_pt)
    axis_title_font = _text(family, axis_title_pt)
    label_font = _text(
        family,
        PANEL_LABEL_PT,
        weight=PANEL_LABEL_WEIGHT,
        style=PANEL_LABEL_STYLE,
    )
    multi = plan.panel_count > 1

    if len(styled.panels) != plan.panel_count:
        raise PanelCountError(
            f"面板数量与布局不符：布局「{plan.layout_name}」需要 {plan.panel_count} 个面板，"
            f"当前图有 {len(styled.panels)} 个。"
        )

    for panel, box in zip(styled.panels, plan.panels, strict=True):
        panel.title_font = title_font
        panel.x_mm = box.x_mm
        panel.y_mm = box.y_mm
        panel.width_mm = box.width_mm
        panel.height_mm = box.height_mm
        if multi:
            panel.panel_label = box.label
            panel.panel_label_font = label_font
        else:
            panel.panel_label = None
            panel.panel_label_font = None

        for note in panel.annotations:
            note.font = annotation_font

        panel.x_axis.line_weight_pt = axis_line_pt
        panel.x_axis.tick_weight_pt = tick_width
        panel.x_axis.tick_font = tick_font
        panel.x_axis.title_font = axis_title_font

        panel.y_axis.line_weight_pt = axis_line_pt
        panel.y_axis.tick_weight_pt = tick_width
        panel.y_axis.tick_font = tick_font
        panel.y_axis.title_font = axis_title_font

    return RestyleResult(
        figure=styled,
        plan=plan,
        font_family=family,
        title_pt=title_pt,
        annotation_pt=annotation_pt,
        tick_label_pt=tick_label_pt,
        axis_title_pt=axis_title_pt,
        axis_line_pt=axis_line_pt,
        tick_line_pt=tick_width,
    )
