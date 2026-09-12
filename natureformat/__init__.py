"""One-click Nature final-artwork restyler for already-assembled figures."""

from .apply import apply_nature_format
from .figure import Figure, load_figure, dump_figure
from .layouts import (
    COLUMN_DOUBLE,
    COLUMN_SINGLE,
    LAYOUT_NAMES,
    plan_layout,
)
from .spec import (
    FONT_ARIAL,
    FONT_HELVETICA,
    MAX_PAGE_HEIGHT_MM,
    SINGLE_COLUMN_WIDTH_MM,
    DOUBLE_COLUMN_WIDTH_MM,
)

__version__ = "0.1.0"

__all__ = [
    "COLUMN_DOUBLE",
    "COLUMN_SINGLE",
    "DOUBLE_COLUMN_WIDTH_MM",
    "FONT_ARIAL",
    "FONT_HELVETICA",
    "Figure",
    "LAYOUT_NAMES",
    "MAX_PAGE_HEIGHT_MM",
    "SINGLE_COLUMN_WIDTH_MM",
    "apply_nature_format",
    "dump_figure",
    "load_figure",
    "plan_layout",
]
