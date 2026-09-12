"""Layout planner: Nature page size + per-panel boxes for the five named layouts."""

from __future__ import annotations

from dataclasses import dataclass

from .errors import PanelCountError, UnknownChoiceError
from .spec import (
    DOUBLE_COLUMN_WIDTH_MM,
    GUTTER_X_MM,
    GUTTER_Y_MM,
    MAX_PAGE_HEIGHT_MM,
    PAGE_MARGIN_BOTTOM_MM,
    PAGE_MARGIN_LEFT_MM,
    PAGE_MARGIN_RIGHT_MM,
    PAGE_MARGIN_TOP_MM,
    PANEL_LABELS,
    SINGLE_COLUMN_WIDTH_MM,
)

COLUMN_SINGLE = "单栏（Single Column）"
COLUMN_DOUBLE = "双栏（Double Column）"
COLUMN_CHOICES = (COLUMN_SINGLE, COLUMN_DOUBLE)

LAYOUT_SINGLE = "单图（一行一图）"
LAYOUT_TWO = "两图一行"
LAYOUT_THREE = "三图一行"
LAYOUT_SIX = "六宫格"
LAYOUT_NINE = "九宫格"
LAYOUT_NAMES = (LAYOUT_SINGLE, LAYOUT_TWO, LAYOUT_THREE, LAYOUT_SIX, LAYOUT_NINE)

PANEL_COUNT_BY_LAYOUT = {
    LAYOUT_SINGLE: 1,
    LAYOUT_TWO: 2,
    LAYOUT_THREE: 3,
    LAYOUT_SIX: 6,
    LAYOUT_NINE: 9,
}

_COLUMN_ALIASES = {
    COLUMN_SINGLE.lower(): COLUMN_SINGLE,
    "单栏": COLUMN_SINGLE,
    "single": COLUMN_SINGLE,
    "single column": COLUMN_SINGLE,
    "single-column": COLUMN_SINGLE,
    "89": COLUMN_SINGLE,
    "89mm": COLUMN_SINGLE,
    COLUMN_DOUBLE.lower(): COLUMN_DOUBLE,
    "双栏": COLUMN_DOUBLE,
    "double": COLUMN_DOUBLE,
    "double column": COLUMN_DOUBLE,
    "double-column": COLUMN_DOUBLE,
    "183": COLUMN_DOUBLE,
    "183mm": COLUMN_DOUBLE,
}

_LAYOUT_ALIASES = {
    LAYOUT_SINGLE.lower(): LAYOUT_SINGLE,
    "单图": LAYOUT_SINGLE,
    "一行一图": LAYOUT_SINGLE,
    "1": LAYOUT_SINGLE,
    LAYOUT_TWO.lower(): LAYOUT_TWO,
    "两图": LAYOUT_TWO,
    "2": LAYOUT_TWO,
    LAYOUT_THREE.lower(): LAYOUT_THREE,
    "三图": LAYOUT_THREE,
    "3": LAYOUT_THREE,
    LAYOUT_SIX.lower(): LAYOUT_SIX,
    "6": LAYOUT_SIX,
    LAYOUT_NINE.lower(): LAYOUT_NINE,
    "9": LAYOUT_NINE,
}


def normalize_column(value: str) -> str:
    key = str(value).strip()
    if key in COLUMN_CHOICES:
        return key
    mapped = _COLUMN_ALIASES.get(key.lower())
    if mapped is None:
        raise UnknownChoiceError(
            "栏宽必须是 单栏（Single Column） 或 双栏（Double Column），"
            f"收到：{value!r}"
        )
    return mapped


def normalize_layout(value: str) -> str:
    key = str(value).strip()
    if key in LAYOUT_NAMES:
        return key
    mapped = _LAYOUT_ALIASES.get(key.lower())
    if mapped is None:
        named = "、".join(LAYOUT_NAMES)
        raise UnknownChoiceError(f"布局必须是 {named}，收到：{value!r}")
    return mapped


def panel_count_for(layout_name: str) -> int:
    return PANEL_COUNT_BY_LAYOUT[normalize_layout(layout_name)]


def grid_for(column_mode: str, layout_name: str) -> tuple[int, int]:
    """Return (n_rows, n_cols). 六宫格 adapts: 3×2 on 单栏, 2×3 on 双栏."""
    column = normalize_column(column_mode)
    layout = normalize_layout(layout_name)
    if layout == LAYOUT_SINGLE:
        return 1, 1
    if layout == LAYOUT_TWO:
        return 1, 2
    if layout == LAYOUT_THREE:
        return 1, 3
    if layout == LAYOUT_SIX:
        if column == COLUMN_SINGLE:
            return 3, 2
        return 2, 3
    return 3, 3


def _round2(value: float) -> float:
    return round(float(value) + 1e-12, 2)


def _split_equal(total: float, count: int, gap: float) -> list[float]:
    """Equal slices that sum with gaps to *total*, at 0.01 mm resolution."""
    if count < 1:
        raise NatureLayoutInternalError("count must be ≥ 1")
    usable = _round2(total - gap * (count - 1))
    raw = usable / count
    sizes = [_round2(raw) for _ in range(count)]
    sizes[-1] = _round2(usable - sum(sizes[:-1]))
    return sizes


class NatureLayoutInternalError(RuntimeError):
    pass


def _panel_aspect(n_rows: int, n_cols: int) -> float:
    """Height / width of one panel box."""
    if n_rows == 1 and n_cols == 1:
        return 0.72
    if n_rows == 1:
        return 0.82
    return 0.78


@dataclass(frozen=True)
class PanelBox:
    index: int
    label: str
    x_mm: float
    y_mm: float
    width_mm: float
    height_mm: float

    def right_mm(self) -> float:
        return _round2(self.x_mm + self.width_mm)

    def bottom_mm(self) -> float:
        return _round2(self.y_mm + self.height_mm)


@dataclass(frozen=True)
class LayoutPlan:
    column_mode: str
    layout_name: str
    page_width_mm: float
    page_height_mm: float
    n_rows: int
    n_cols: int
    panels: tuple[PanelBox, ...]

    @property
    def panel_count(self) -> int:
        return len(self.panels)


def plan_layout(
    column_mode: str,
    layout_name: str,
    *,
    panel_count: int | None = None,
) -> LayoutPlan:
    """Return page + panel geometry for one built-in layout.

    Page width is exactly 89 mm (单栏) or 183 mm (双栏). Height is ≤ 247 mm.
    If *panel_count* is given and does not match the layout, raise PanelCountError
    instead of dropping or inventing panels.
    """
    column = normalize_column(column_mode)
    layout = normalize_layout(layout_name)
    expected = PANEL_COUNT_BY_LAYOUT[layout]
    if panel_count is not None and int(panel_count) != expected:
        raise PanelCountError(
            f"面板数量与布局不符：布局「{layout}」需要 {expected} 个面板，"
            f"当前图有 {int(panel_count)} 个。"
            "不会丢弃多余面板，也不会静默少排。"
        )

    page_width = (
        SINGLE_COLUMN_WIDTH_MM if column == COLUMN_SINGLE else DOUBLE_COLUMN_WIDTH_MM
    )
    n_rows, n_cols = grid_for(column, layout)

    inner_width = page_width - PAGE_MARGIN_LEFT_MM - PAGE_MARGIN_RIGHT_MM
    widths = _split_equal(inner_width, n_cols, GUTTER_X_MM)

    aspect = _panel_aspect(n_rows, n_cols)
    raw_height = _round2(widths[0] * aspect)
    inner_height = n_rows * raw_height + GUTTER_Y_MM * (n_rows - 1)
    page_height = _round2(PAGE_MARGIN_TOP_MM + PAGE_MARGIN_BOTTOM_MM + inner_height)
    if page_height > MAX_PAGE_HEIGHT_MM:
        usable_h = MAX_PAGE_HEIGHT_MM - PAGE_MARGIN_TOP_MM - PAGE_MARGIN_BOTTOM_MM
        heights = _split_equal(usable_h, n_rows, GUTTER_Y_MM)
        page_height = MAX_PAGE_HEIGHT_MM
    else:
        heights = [raw_height] * n_rows
        # Absorb 0.01 mm rounding so the last row still fits the computed page.
        used = _round2(sum(heights) + GUTTER_Y_MM * (n_rows - 1))
        target = _round2(page_height - PAGE_MARGIN_TOP_MM - PAGE_MARGIN_BOTTOM_MM)
        heights[-1] = _round2(heights[-1] + (target - used))

    panels: list[PanelBox] = []
    y = PAGE_MARGIN_TOP_MM
    index = 0
    for row in range(n_rows):
        x = PAGE_MARGIN_LEFT_MM
        for col in range(n_cols):
            panels.append(
                PanelBox(
                    index=index,
                    label=PANEL_LABELS[index],
                    x_mm=_round2(x),
                    y_mm=_round2(y),
                    width_mm=widths[col],
                    height_mm=heights[row],
                )
            )
            x = _round2(x + widths[col] + GUTTER_X_MM)
            index += 1
        y = _round2(y + heights[row] + GUTTER_Y_MM)

    return LayoutPlan(
        column_mode=column,
        layout_name=layout,
        page_width_mm=float(page_width),
        page_height_mm=float(page_height),
        n_rows=n_rows,
        n_cols=n_cols,
        panels=tuple(panels),
    )
