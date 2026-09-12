"""LabTalk generator is shipped code; COM attach is optional."""

from __future__ import annotations

from natureformat.layouts import COLUMN_SINGLE, plan_layout
from natureformat.origin_adapter import labtalk_restyle_script, mm_to_inch, probe_origin
from natureformat.spec import SINGLE_COLUMN_WIDTH_MM


def test_labtalk_sets_page_fonts_and_axis_not_markers() -> None:
    plan = plan_layout(COLUMN_SINGLE, "六宫格")
    script = labtalk_restyle_script(
        plan,
        font_family="Arial",
        axis_line_pt=0.5,
        tick_label_pt=6.0,
        tick_line_pt=0.5,
    )
    assert "page.updatetoprinter = 0;" in script
    assert f"page.width = {mm_to_inch(SINGLE_COLUMN_WIDTH_MM)}*page.resx;" in script
    assert script.strip().endswith("// end NatureFormat") or "end NatureFormat" in script
    assert "layer.unit = 4;" in script
    assert "layer.x.thickness = 0.5;" in script
    assert "layer.x.font.size = 6.0;" in script
    assert "layer.text.bold = 1" in script
    assert "layer.text.italic = 0" in script
    assert mm_to_inch(SINGLE_COLUMN_WIDTH_MM) == round(SINGLE_COLUMN_WIDTH_MM / 25.4, 4)
    lowered = script.lower()
    assert "color(" not in lowered
    assert "set %c" not in lowered
    assert "symbol" not in lowered
    assert "marker" not in lowered or "does not change plot data, marker shape" in lowered
    assert script.count("page.active") == 6


def test_inspect_active_graph_does_not_raise() -> None:
    from natureformat.origin_adapter import inspect_active_graph, running_inside_origin

    info = inspect_active_graph()
    assert info is None or (isinstance(info, dict) and "name" in info and "layers" in info)
    assert running_inside_origin() in (True, False)


def test_probe_origin_returns_tuple() -> None:
    ok, detail = probe_origin()
    assert isinstance(ok, bool)
    assert isinstance(detail, str)
    assert detail
