"""User-facing errors. Panel-count mismatch is never a silent drop."""

from __future__ import annotations


class NatureFormatError(ValueError):
    """Base error for this tool."""


class UnknownChoiceError(NatureFormatError):
    """Column mode or layout name is not one of the built-in choices."""


class PanelCountError(NatureFormatError):
    """Assembled figure panel count does not match the chosen layout."""


class NatureSpecError(NatureFormatError):
    """A requested style value is outside the Nature final-artwork window."""


class OriginUnavailableError(NatureFormatError):
    """Origin COM / originpro could not be attached."""
