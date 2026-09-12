"""Deterministic human-readable report used by the CLI and the UI."""

from __future__ import annotations

from .apply import RestyleResult
from .layouts import LayoutPlan


def format_plan(plan: LayoutPlan) -> str:
    lines = [
        f"column_mode: {plan.column_mode}",
        f"layout: {plan.layout_name}",
        f"page_width_mm: {plan.page_width_mm:.2f}",
        f"page_height_mm: {plan.page_height_mm:.2f}",
        f"panel_count: {plan.panel_count}",
        f"grid: {plan.n_rows}x{plan.n_cols}",
    ]
    for box in plan.panels:
        lines.append(
            f"panel {box.label}: x_mm={box.x_mm:.2f} y_mm={box.y_mm:.2f} "
            f"width_mm={box.width_mm:.2f} height_mm={box.height_mm:.2f}"
        )
    return "\n".join(lines)


def format_result(result: RestyleResult) -> str:
    figure = result.figure
    lines = [
        format_plan(result.plan),
        f"font_family: {result.font_family}",
        f"title_pt: {result.title_pt:.2f}",
        f"annotation_pt: {result.annotation_pt:.2f}",
        f"tick_label_pt: {result.tick_label_pt:.2f}",
        f"axis_title_pt: {result.axis_title_pt:.2f}",
        f"axis_line_pt: {result.axis_line_pt:.2f}",
        f"tick_line_pt: {result.tick_line_pt:.2f}",
        f"preserved_series: {sum(len(p.series) for p in figure.panels)}",
    ]
    return "\n".join(lines)
