"""Thin Origin COM / LabTalk adapter. Core restyle never depends on Origin."""

from __future__ import annotations

from .apply import RestyleResult, apply_nature_format
from .demo import assembled_figure
from .errors import OriginUnavailableError, PanelCountError
from .layouts import LayoutPlan, plan_layout
from .report import format_result
from .spec import (
    DEFAULT_AXIS_LINE_PT,
    DEFAULT_TICK_LABEL_PT,
    FONT_ARIAL,
    PANEL_LABEL_PT,
)


def mm_to_inch(mm: float) -> float:
    return round(float(mm) / 25.4, 4)


def page_size_labtalk(plan: LayoutPlan) -> str:
    """Short script. Origin can truncate a long multi-layer script before a trailing size line."""
    return (
        "page.updatetoprinter = 0; "
        f"page.width = {mm_to_inch(plan.page_width_mm)}*page.resx; "
        f"page.height = {mm_to_inch(plan.page_height_mm)}*page.resy;"
    )


def labtalk_restyle_script(
    plan: LayoutPlan,
    *,
    font_family: str = FONT_ARIAL,
    title_pt: float = 7.0,
    annotation_pt: float = 6.0,
    tick_label_pt: float = DEFAULT_TICK_LABEL_PT,
    axis_title_pt: float = 7.0,
    axis_line_pt: float = DEFAULT_AXIS_LINE_PT,
    tick_line_pt: float = DEFAULT_AXIS_LINE_PT,
) -> str:
    """LabTalk that sets page size, fonts, and axis weights — never plot color/symbol.

    Origin's page.width is printer dots; inches = page.width/page.resx.
    """
    lines = [
        "// NatureFormat: page size, fonts, axis weights only.",
        "// Does not change plot data, marker shape, or series color.",
        "page.updatetoprinter = 0;",
    ]
    for box in plan.panels:
        layer = box.index + 1
        lines.append(f"page.active = {layer};")
        lines.append("layer.unit = 4;")  # millimetres
        lines.append(f"layer.left = {box.x_mm};")
        lines.append(f"layer.top = {box.y_mm};")
        lines.append(f"layer.width = {box.width_mm};")
        lines.append(f"layer.height = {box.height_mm};")
        lines.append(f"layer.x.thickness = {axis_line_pt};")
        lines.append(f"layer.y.thickness = {axis_line_pt};")
        lines.append(f"layer.x.ticks.width = {tick_line_pt};")
        lines.append(f"layer.y.ticks.width = {tick_line_pt};")
        lines.append(f"layer.x.font=font({font_family});")
        lines.append(f"layer.y.font=font({font_family});")
        lines.append(f"layer.x.font.size = {tick_label_pt};")
        lines.append(f"layer.y.font.size = {tick_label_pt};")
        lines.append(f"layer.x.label.font=font({font_family});")
        lines.append(f"layer.y.label.font=font({font_family});")
        lines.append(f"layer.x.label.size = {axis_title_pt};")
        lines.append(f"layer.y.label.size = {axis_title_pt};")
        lines.append(f"layer.title.font=font({font_family});")
        lines.append(f"layer.title.size = {title_pt};")
        if plan.panel_count > 1:
            lines.append(
                f'layer.text = "{box.label}"; layer.text.fsize = {PANEL_LABEL_PT}; '
                "layer.text.bold = 1; layer.text.italic = 0;"
            )
        lines.append(f"// panel {box.label} box mm: {box.x_mm},{box.y_mm},{box.width_mm},{box.height_mm}")
        lines.append(f"// annotation target size {annotation_pt} pt")
    lines.append(page_size_labtalk(plan))
    lines.append("// end NatureFormat")
    return "\n".join(lines) + "\n"


def probe_origin() -> tuple[bool, str]:
    """Try to attach Origin. Returns (ok, detail). Never raises. Does not show the GUI."""
    try:
        import originpro as op  # type: ignore
    except Exception as exc:
        com_detail = _probe_com()
        return False, f"import originpro failed: {exc}; COM: {com_detail}"

    try:
        names = [name for name in ("lt_exec", "new_graph", "new_book") if hasattr(op, name)]
        if not names:
            return False, "originpro imported but missing lt_exec/new_graph"
        return True, f"originpro available ({', '.join(names)})"
    except Exception as exc:
        return False, f"originpro imported but attach failed: {exc}"


def _probe_com() -> str:
    try:
        import win32com.client  # type: ignore
    except Exception as exc:
        return f"win32com missing ({exc})"
    for progid in ("Origin.ApplicationSI", "Origin.Application"):
        try:
            win32com.client.Dispatch(progid)
            return f"Dispatch({progid}) succeeded"
        except Exception as exc:
            last = f"Dispatch({progid}) failed: {exc}"
    return last


def running_inside_origin() -> bool:
    """True only in Origin's embedded Python (PyOrigin), not external COM."""
    try:
        import PyOrigin  # type: ignore  # noqa: F401

        return True
    except Exception:
        return False


def inspect_active_graph() -> dict | None:
    """Return {name, layers} for the active Origin graph, or None."""
    try:
        import originpro as op  # type: ignore
    except Exception:
        return None
    try:
        gp = op.find_graph()
        if gp is None:
            return None
        return {"name": str(gp.name), "layers": int(len(gp))}
    except Exception:
        return None


def apply_to_active_origin(
    column_mode: str,
    layout_name: str,
    *,
    axis_line_pt: float = DEFAULT_AXIS_LINE_PT,
    tick_label_pt: float = DEFAULT_TICK_LABEL_PT,
    font_family: str = FONT_ARIAL,
) -> str:
    """Apply restyle to the active Origin graph if COM works.

    Always builds the same LabTalk from the Origin-free planner. If Origin
    cannot be attached, raises OriginUnavailableError with the probe text.
    """
    ok, detail = probe_origin()
    plan = plan_layout(column_mode, layout_name)
    script = labtalk_restyle_script(
        plan,
        font_family=font_family,
        axis_line_pt=axis_line_pt,
        tick_label_pt=tick_label_pt,
        tick_line_pt=axis_line_pt,
    )

    dummy = assembled_figure(plan.panel_count)
    result = apply_nature_format(
        dummy,
        column_mode,
        layout_name,
        font_family=font_family,
        axis_line_pt=axis_line_pt,
        tick_label_pt=tick_label_pt,
    )

    if not ok:
        raise OriginUnavailableError(
            "无法连接 Origin。已生成 LabTalk，可粘贴到 Origin 脚本窗口。\n"
            f"原因：{detail}\n"
            f"{script}"
        )

    info = inspect_active_graph()
    if info is None:
        raise OriginUnavailableError("请先在 Origin 里打开并选中一张已经组好的图。")
    if int(info["layers"]) != plan.panel_count:
        raise PanelCountError(
            f"面板数量与布局不符：布局「{plan.layout_name}」需要 {plan.panel_count} 个图层，"
            f"当前图 {info['name']} 有 {info['layers']} 个。"
            "不会丢弃多余面板，也不会静默少排。"
        )

    try:
        import originpro as op  # type: ignore

        gp = op.find_graph()
        if gp is not None:
            gp.activate()
    except Exception:
        pass

    executed = _exec_labtalk(script)
    if executed is not True:
        raise OriginUnavailableError(
            "originpro 已导入，但未能在当前图执行 LabTalk。\n"
            f"原因：{executed}\n"
            f"{script}"
        )
    _exec_labtalk(page_size_labtalk(plan))
    return format_result(result) + "\n" + script


def _exec_labtalk(script: str) -> bool | str:
    try:
        import originpro as op  # type: ignore
    except Exception as exc:
        return str(exc)

    for name in ("lt_exec", "lt_execute", "execute"):
        fn = getattr(op, name, None)
        if callable(fn):
            try:
                fn(script)
                return True
            except Exception as exc:
                return f"{name} failed: {exc}"
    return "originpro has no lt_exec/lt_execute/execute"


def _graph_snapshot(op, gp) -> dict:
    """Page size in mm, fonts, axis weights, and first-layer plot color/symbol."""
    snap: dict = {
        "page_width_mm": op.lt_float("page.width/page.resx*25.4"),
        "page_height_mm": op.lt_float("page.height/page.resy*25.4"),
        "x_label_size": op.lt_float("layer.x.label.size"),
        "y_label_size": op.lt_float("layer.y.label.size"),
        "x_thickness": op.lt_float("layer.x.thickness"),
        "y_thickness": op.lt_float("layer.y.thickness"),
        "layer_count": len(gp),
        "layer_width": op.lt_float("layer.width"),
        "layer_unit": op.lt_float("layer.unit"),
        "graph_active": gp.is_active(),
        "graph_name": gp.name,
        "page_width_in": op.lt_float("page.width/page.resx"),
        "plots": [],
    }
    layer = gp[0]
    for plot in layer.plot_list():
        snap["plots"].append(
            {
                "color": plot.color,
                "symbol_kind": plot.symbol_kind,
            }
        )
    return snap


def apply_to_throwaway_graph(
    column_mode: str,
    layout_name: str,
    *,
    axis_line_pt: float = DEFAULT_AXIS_LINE_PT,
    tick_label_pt: float = DEFAULT_TICK_LABEL_PT,
    font_family: str = FONT_ARIAL,
) -> str:
    """Create a hidden 6-layer scatter graph, restyle it, snapshot, then destroy it."""
    import originpro as op  # type: ignore

    plan = plan_layout(column_mode, layout_name)
    script = labtalk_restyle_script(
        plan,
        font_family=font_family,
        axis_line_pt=axis_line_pt,
        tick_label_pt=tick_label_pt,
        tick_line_pt=axis_line_pt,
    )
    result = _offline_result(column_mode, layout_name)

    book = None
    graph = None
    try:
        book = op.new_book("w", lname="NatureFormat_tmp_book", hidden=True)
        wks = book[0]
        wks.from_list(0, [0.0, 1.0, 2.0, 3.0, 4.0])
        wks.from_list(1, [0.0, 1.1, 2.0, 2.6, 3.1])
        wks.from_list(2, [0.2, 0.8, 1.5, 2.1, 2.4])
        graph = op.new_graph(lname="NatureFormat_tmp_graph", hidden=True)
        graph.activate()
        op.lt_exec("page.updatetoprinter = 0;")
        op.lt_exec(
            f"page.width = {mm_to_inch(plan.page_width_mm)}*page.resx; "
            f"page.height = {mm_to_inch(plan.page_height_mm)}*page.resy;"
        )
        while len(graph) < plan.panel_count:
            graph.add_layer(0)
        for i in range(plan.panel_count):
            layer = graph[i]
            p1 = layer.add_plot(wks, 1, 0, type="s")
            p2 = layer.add_plot(wks, 2, 0, type="s")
            p1.color = "#D62728"
            p2.color = "#1F77B4"
            p1.symbol_kind = 2  # circle
            p2.symbol_kind = 1  # square
            layer.rescale()
        graph.activate()
        before = _graph_snapshot(op, graph)
        ok = op.lt_exec(script)
        graph.activate()
        op.lt_exec(page_size_labtalk(plan))
        graph.activate()
        after = _graph_snapshot(op, graph)
        if ok is False:
            raise OriginUnavailableError("lt_exec returned False")
        return (
            "ORIGIN_APPLY_OK\n"
            f"{format_result(result)}\n"
            f"before={before}\n"
            f"after={after}\n"
            f"{script}"
        )
    finally:
        if graph is not None:
            try:
                graph.destroy()
            except Exception:
                pass
        if book is not None:
            try:
                book.destroy()
            except Exception:
                pass


def origin_apply_evidence(column_mode: str, layout_name: str) -> str:
    """For the verification capture. Never raises. Uses a throwaway graph only."""
    ok, detail = probe_origin()
    plan = plan_layout(column_mode, layout_name)
    script = labtalk_restyle_script(plan)
    if not ok:
        return (
            "ORIGIN_UNAVAILABLE\n"
            f"{detail}\n"
            f"{format_result(_offline_result(column_mode, layout_name))}\n"
            f"{script}"
        )
    try:
        return apply_to_throwaway_graph(column_mode, layout_name)
    except Exception as exc:
        return (
            "ORIGIN_UNAVAILABLE\n"
            f"{exc}\n"
            f"{format_result(_offline_result(column_mode, layout_name))}\n"
            f"{script}"
        )


def _offline_result(column_mode: str, layout_name: str) -> RestyleResult:
    plan = plan_layout(column_mode, layout_name)
    return apply_nature_format(assembled_figure(plan.panel_count), column_mode, layout_name)
