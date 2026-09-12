"""Origin-free description of an already-assembled figure."""

from __future__ import annotations

import copy
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

MARKER_CIRCLE = "circle"
MARKER_SQUARE = "square"
_MARKER_ALIASES = {
    "circle": MARKER_CIRCLE,
    "o": MARKER_CIRCLE,
    "圆": MARKER_CIRCLE,
    "圆形": MARKER_CIRCLE,
    "square": MARKER_SQUARE,
    "s": MARKER_SQUARE,
    "方": MARKER_SQUARE,
    "方形": MARKER_SQUARE,
}


def canonical_marker(value: str) -> str:
    key = str(value).strip().lower()
    if key in _MARKER_ALIASES:
        return _MARKER_ALIASES[key]
    return str(value)


@dataclass
class TextStyle:
    family: str
    size_pt: float
    weight: str = "normal"
    style: str = "normal"


@dataclass
class Series:
    name: str
    x: list[float]
    y: list[float]
    marker: str
    color: str


@dataclass
class Annotation:
    text: str
    x: float
    y: float
    font: TextStyle


@dataclass
class AxisStyle:
    title: str
    line_weight_pt: float
    tick_weight_pt: float
    tick_font: TextStyle
    title_font: TextStyle


@dataclass
class Panel:
    title: str
    title_font: TextStyle
    annotations: list[Annotation]
    series: list[Series]
    x_axis: AxisStyle
    y_axis: AxisStyle
    panel_label: str | None = None
    panel_label_font: TextStyle | None = None
    x_mm: float | None = None
    y_mm: float | None = None
    width_mm: float | None = None
    height_mm: float | None = None


@dataclass
class Figure:
    width_mm: float
    height_mm: float
    panels: list[Panel] = field(default_factory=list)

    def copy(self) -> Figure:
        return copy.deepcopy(self)

    def plot_identity(self) -> tuple:
        """Data values, marker shapes, and series colors — the fields apply must not touch."""
        identity = []
        for panel in self.panels:
            for series in panel.series:
                identity.append(
                    (
                        tuple(series.x),
                        tuple(series.y),
                        canonical_marker(series.marker),
                        series.color,
                        series.name,
                    )
                )
        return tuple(identity)


def _text_style(data: dict[str, Any] | None, default_family: str = "Times New Roman", default_size: float = 12.0) -> TextStyle:
    payload = data or {}
    return TextStyle(
        family=str(payload.get("family", default_family)),
        size_pt=float(payload.get("size_pt", default_size)),
        weight=str(payload.get("weight", "normal")),
        style=str(payload.get("style", "normal")),
    )


def _axis(data: dict[str, Any] | None) -> AxisStyle:
    payload = data or {}
    return AxisStyle(
        title=str(payload.get("title", "")),
        line_weight_pt=float(payload.get("line_weight_pt", 2.0)),
        tick_weight_pt=float(payload.get("tick_weight_pt", 1.5)),
        tick_font=_text_style(payload.get("tick_font")),
        title_font=_text_style(payload.get("title_font")),
    )


def _series(data: dict[str, Any]) -> Series:
    return Series(
        name=str(data.get("name", "")),
        x=[float(v) for v in data.get("x", [])],
        y=[float(v) for v in data.get("y", [])],
        marker=canonical_marker(str(data.get("marker", MARKER_CIRCLE))),
        color=str(data.get("color", "#000000")),
    )


def _annotation(data: dict[str, Any]) -> Annotation:
    return Annotation(
        text=str(data.get("text", "")),
        x=float(data.get("x", 0.0)),
        y=float(data.get("y", 0.0)),
        font=_text_style(data.get("font")),
    )


def figure_from_dict(data: dict[str, Any]) -> Figure:
    panels = []
    for raw in data.get("panels", []):
        panels.append(
            Panel(
                title=str(raw.get("title", "")),
                title_font=_text_style(raw.get("title_font")),
                annotations=[_annotation(item) for item in raw.get("annotations", [])],
                series=[_series(item) for item in raw.get("series", [])],
                x_axis=_axis(raw.get("x_axis")),
                y_axis=_axis(raw.get("y_axis")),
                panel_label=raw.get("panel_label"),
                panel_label_font=_text_style(raw["panel_label_font"]) if raw.get("panel_label_font") else None,
                x_mm=float(raw["x_mm"]) if raw.get("x_mm") is not None else None,
                y_mm=float(raw["y_mm"]) if raw.get("y_mm") is not None else None,
                width_mm=float(raw["width_mm"]) if raw.get("width_mm") is not None else None,
                height_mm=float(raw["height_mm"]) if raw.get("height_mm") is not None else None,
            )
        )
    return Figure(
        width_mm=float(data.get("width_mm", 0.0)),
        height_mm=float(data.get("height_mm", 0.0)),
        panels=panels,
    )


def figure_to_dict(figure: Figure) -> dict[str, Any]:
    return asdict(figure)


def load_figure(path: str | Path) -> Figure:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"图描述必须是 JSON 对象：{path}")
    return figure_from_dict(payload)


def dump_figure(figure: Figure, path: str | Path) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(figure_to_dict(figure), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return target
