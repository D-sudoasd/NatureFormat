"""Nature final-artwork constants.

Source of numbers: Nature final submission / Guide to preparing final artwork,
as fixed by this project's plan (89 / 183 mm, height ≤ 247 mm).
These are production sizes, not the initial-submission 90 / 180 mm pair.
"""

from __future__ import annotations

SINGLE_COLUMN_WIDTH_MM = 89.0
DOUBLE_COLUMN_WIDTH_MM = 183.0
MAX_PAGE_HEIGHT_MM = 247.0

FONT_ARIAL = "Arial"
FONT_HELVETICA = "Helvetica"
NATURE_FONTS = (FONT_ARIAL, FONT_HELVETICA)

TEXT_SIZE_PT_MIN = 5.0
TEXT_SIZE_PT_MAX = 7.0
DEFAULT_TITLE_PT = 7.0
DEFAULT_ANNOTATION_PT = 6.0
DEFAULT_TICK_LABEL_PT = 6.0
DEFAULT_AXIS_TITLE_PT = 7.0

PANEL_LABEL_PT = 8.0
PANEL_LABEL_WEIGHT = "bold"
PANEL_LABEL_STYLE = "normal"  # upright, not italic
PANEL_LABELS = "abcdefghijklmnopqrstuvwxyz"

STROKE_PT_MIN = 0.25
STROKE_PT_MAX = 1.0
DEFAULT_AXIS_LINE_PT = 0.5
DEFAULT_TICK_LINE_PT = 0.5

# Page chrome in millimetres. Tight enough for Nature, wide enough for 6 pt ticks.
PAGE_MARGIN_LEFT_MM = 2.0
PAGE_MARGIN_RIGHT_MM = 2.0
PAGE_MARGIN_TOP_MM = 4.0
PAGE_MARGIN_BOTTOM_MM = 2.0
GUTTER_X_MM = 4.0
GUTTER_Y_MM = 5.0
