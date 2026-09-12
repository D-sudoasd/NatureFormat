"""Built-in already-assembled demo figure (six panels, circle + square)."""

from __future__ import annotations

from .figure import (
    MARKER_CIRCLE,
    MARKER_SQUARE,
    Annotation,
    AxisStyle,
    Figure,
    Panel,
    Series,
    TextStyle,
)


def _messy_font(size: float = 12.0) -> TextStyle:
    return TextStyle(family="Times New Roman", size_pt=size, weight="normal", style="italic")


def _axis(title: str) -> AxisStyle:
    return AxisStyle(
        title=title,
        line_weight_pt=2.0,
        tick_weight_pt=1.8,
        tick_font=_messy_font(10.0),
        title_font=_messy_font(11.0),
    )


def _panel(index: int) -> Panel:
    offset = float(index)
    return Panel(
        title=f"Panel {index + 1} draft title",
        title_font=_messy_font(14.0),
        annotations=[
            Annotation(text="note", x=0.25, y=0.80, font=_messy_font(11.0)),
        ],
        series=[
            Series(
                name="alloy A",
                x=[0.0, 1.0, 2.0, 3.0, 4.0],
                y=[0.0 + offset * 0.1, 1.1, 2.0, 2.6, 3.1],
                marker=MARKER_CIRCLE,
                color="#D62728",
            ),
            Series(
                name="alloy B",
                x=[0.0, 1.0, 2.0, 3.0, 4.0],
                y=[0.2 + offset * 0.05, 0.8, 1.5, 2.1, 2.4],
                marker=MARKER_SQUARE,
                color="#1F77B4",
            ),
        ],
        x_axis=_axis("Strain (%)"),
        y_axis=_axis("Stress (MPa)"),
    )


def assembled_figure(panel_count: int) -> Figure:
    return Figure(width_mm=160.0, height_mm=120.0, panels=[_panel(i) for i in range(panel_count)])
