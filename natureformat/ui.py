"""Nature-style one-click UI. Same planner/apply as the CLI and Origin App."""

from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox

from .apply import apply_nature_format
from .demo import assembled_figure
from .errors import NatureFormatError, OriginUnavailableError, PanelCountError
from .figure import dump_figure, load_figure
from .layouts import (
    COLUMN_CHOICES,
    COLUMN_DOUBLE,
    COLUMN_SINGLE,
    LAYOUT_NAMES,
    LAYOUT_SIX,
    grid_for,
    panel_count_for,
    plan_layout,
)
from .origin_adapter import inspect_active_graph, running_inside_origin
from .report import format_result
from .spec import (
    DEFAULT_AXIS_LINE_PT,
    DEFAULT_TICK_LABEL_PT,
    FONT_ARIAL,
    STROKE_PT_MAX,
    STROKE_PT_MIN,
    TEXT_SIZE_PT_MAX,
    TEXT_SIZE_PT_MIN,
)

LAYOUT_CHOICES = LAYOUT_NAMES

PAPER = "#F6F1E8"
INK = "#1C1917"
MUTED = "#6F675F"
LINE = "#E4DCD1"
WHITE = "#FFFCF7"
ACCENT = "#9B1B1B"
ACCENT_DARK = "#741414"
OK = "#215C45"
WARN = "#9A4F12"
CHIP = "#EFE8DC"


def restyle_path(path: str | Path, column_mode: str, layout_name: str, **opts):
    figure = load_figure(path)
    return apply_nature_format(figure, column_mode, layout_name, **opts)


def _enable_dpi() -> None:
    try:
        from ctypes import windll

        windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        return


def _font(*parts) -> tuple:
    return parts


class SelectCard(tk.Frame):
    def __init__(self, master, variable: tk.StringVar, value: str, command, **pack):
        super().__init__(master, bg=WHITE, highlightthickness=2, highlightbackground=LINE, cursor="hand2")
        self.variable = variable
        self.value = value
        self._command = command
        self.columnconfigure(1, weight=1)
        self.bind("<Button-1>", self._pick)

    def _pick(self, _event=None) -> None:
        self.variable.set(self.value)
        self._command()

    def refresh(self) -> None:
        on = self.variable.get() == self.value
        self.configure(highlightbackground=ACCENT if on else LINE, bg=WHITE)
        for child in self.winfo_children():
            try:
                child.configure(bg=WHITE)
            except tk.TclError:
                pass


class NatureFormatApp:
    def __init__(self, root: tk.Tk, *, origin_mode: bool = False) -> None:
        self.root = root
        self.origin_mode = origin_mode or running_inside_origin()
        self.root.title("Nature 一键排版" + ("  ·  Origin App" if self.origin_mode else ""))
        self.root.configure(bg=PAPER)
        self.root.minsize(460, 700)
        self.root.geometry("500x780")
        self.column = tk.StringVar(value=COLUMN_SINGLE)
        self.layout = tk.StringVar(value=LAYOUT_SIX)
        self.axis_line = tk.DoubleVar(value=DEFAULT_AXIS_LINE_PT)
        self.tick_label = tk.DoubleVar(value=DEFAULT_TICK_LABEL_PT)
        self.figure_path = tk.StringVar(value="")
        self._cards: list[SelectCard] = []
        self._build()
        self._refresh()

    def _label(self, parent, text, size=11, color=INK, weight="normal", **kw) -> tk.Label:
        return tk.Label(
            parent,
            text=text,
            bg=parent.cget("bg") if isinstance(parent.cget("bg"), str) else PAPER,
            fg=color,
            font=_font("Microsoft YaHei UI", size, weight),
            **kw,
        )

    def _build(self) -> None:
        header = tk.Frame(self.root, bg=INK, padx=22, pady=14)
        header.pack(fill="x")
        tk.Label(
            header,
            text="Nature 一键排版",
            bg=INK,
            fg=WHITE,
            font=_font("Microsoft YaHei UI", 18, "bold"),
        ).pack(anchor="w")
        tk.Label(
            header,
            text="只改尺寸、字体和轴体。数据点、圆形/方形标记和配色保持原样。",
            bg=INK,
            fg="#E8D5D5",
            font=_font("Microsoft YaHei UI", 10),
            wraplength=420,
            justify="left",
        ).pack(anchor="w", pady=(6, 0))

        footer = tk.Frame(self.root, bg=PAPER, padx=20, pady=12)
        footer.pack(side="bottom", fill="x")
        body = tk.Frame(self.root, bg=PAPER, padx=20, pady=12)
        body.pack(fill="both", expand=True)

        self.status = tk.Label(
            body,
            text="",
            bg=CHIP,
            fg=INK,
            font=_font("Microsoft YaHei UI", 10),
            wraplength=420,
            justify="left",
            padx=12,
            pady=8,
            anchor="w",
        )
        self.status.pack(fill="x", pady=(0, 8))

        self._section(body, "版面")
        cols = tk.Frame(body, bg=PAPER)
        cols.pack(fill="x", pady=(2, 8))
        cols.columnconfigure(0, weight=1)
        cols.columnconfigure(1, weight=1)
        self._column_card(cols, COLUMN_SINGLE, "89 mm", "适合单栏插图", 0)
        self._column_card(cols, COLUMN_DOUBLE, "183 mm", "适合通栏大图", 1)

        self._section(body, "布局  ·  图层数必须一致")
        row1 = tk.Frame(body, bg=PAPER)
        row1.pack(fill="x", pady=(4, 0))
        for name in LAYOUT_CHOICES[:3]:
            self._layout_card(row1, name)
        row2 = tk.Frame(body, bg=PAPER)
        row2.pack(fill="x", pady=(0, 8))
        for name in LAYOUT_CHOICES[3:]:
            self._layout_card(row2, name)
        tk.Frame(row2, bg=PAPER).pack(side="left", fill="both", expand=True, padx=4, pady=4)

        self._section(footer, "轴体 / 轴上数字，可分开调")
        sliders = tk.Frame(footer, bg=PAPER)
        sliders.pack(fill="x", pady=(0, 6))
        sliders.columnconfigure(0, weight=1)
        sliders.columnconfigure(1, weight=1)
        left = tk.Frame(sliders, bg=PAPER)
        right = tk.Frame(sliders, bg=PAPER)
        left.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        right.grid(row=0, column=1, sticky="ew", padx=(8, 0))
        self.axis_readout = self._slider(left, "轴体线宽", self.axis_line, STROKE_PT_MIN, STROKE_PT_MAX, "pt")
        self.tick_readout = self._slider(right, "轴上数字", self.tick_label, TEXT_SIZE_PT_MIN, TEXT_SIZE_PT_MAX, "pt")

        if not self.origin_mode:
            files = tk.Frame(footer, bg=PAPER)
            files.pack(fill="x", pady=(0, 8))
            tk.Entry(
                files,
                textvariable=self.figure_path,
                font=_font("Microsoft YaHei UI", 9),
                relief="flat",
                highlightthickness=1,
                highlightbackground=LINE,
                bg=WHITE,
            ).pack(side="left", fill="x", expand=True, ipady=5, padx=(0, 8))
            self._ghost_btn(files, "打开 JSON", self._open).pack(side="left")

        self.apply_btn = tk.Button(
            footer,
            text="一键套用到当前 Origin 图" if self.origin_mode else "一键套用 Nature 格式",
            command=self._apply,
            bg=ACCENT,
            fg=WHITE,
            activebackground=ACCENT_DARK,
            activeforeground=WHITE,
            font=_font("Microsoft YaHei UI", 12, "bold"),
            relief="flat",
            cursor="hand2",
            pady=10,
            bd=0,
        )
        self.apply_btn.pack(fill="x")
        self.preview = tk.Label(
            footer,
            text="",
            bg=PAPER,
            fg=MUTED,
            font=_font("Microsoft YaHei UI", 8),
            wraplength=440,
            justify="left",
            anchor="w",
        )
        self.preview.pack(fill="x", pady=(8, 0))

    def _section(self, parent, text: str) -> None:
        tk.Label(
            parent,
            text=text,
            bg=PAPER,
            fg=MUTED,
            font=_font("Microsoft YaHei UI", 9),
            anchor="w",
        ).pack(fill="x")

    def _column_card(self, parent, value: str, size: str, hint: str, col: int) -> None:
        card = SelectCard(parent, self.column, value, self._refresh)
        card.grid(row=0, column=col, sticky="nsew", padx=(0, 8) if col == 0 else (8, 0))
        title = tk.Label(card, text=value.split("（")[0], bg=WHITE, fg=INK, font=_font("Microsoft YaHei UI", 12, "bold"))
        title.pack(anchor="w", padx=12, pady=(8, 0))
        tk.Label(card, text=f"{size}  ·  {hint}", bg=WHITE, fg=MUTED, font=_font("Microsoft YaHei UI", 9)).pack(anchor="w", padx=12, pady=(0, 10))
        for w in card.winfo_children():
            w.bind("<Button-1>", card._pick)
        self._cards.append(card)

    def _layout_card(self, parent, name: str) -> None:
        card = SelectCard(parent, self.layout, name, self._refresh)
        card.pack(side="left", fill="both", expand=True, padx=4, pady=4)
        canvas = tk.Canvas(card, width=78, height=36, bg=WHITE, highlightthickness=0)
        canvas.pack(padx=6, pady=(6, 0))
        self._draw_thumb(canvas, name)
        n = panel_count_for(name)
        tk.Label(card, text=f"{name}  ·  {n} 个", bg=WHITE, fg=INK, font=_font("Microsoft YaHei UI", 8)).pack(padx=4, pady=(0, 8))
        for w in card.winfo_children():
            w.bind("<Button-1>", card._pick)
        canvas.bind("<Button-1>", card._pick)
        self._cards.append(card)

    def _draw_thumb(self, canvas: tk.Canvas, layout: str) -> None:
        rows, cols = grid_for(self.column.get(), layout)
        pad, gap = 6, 3
        w, h = 78, 36
        cw = (w - 2 * pad - gap * (cols - 1)) / cols
        ch = (h - 2 * pad - gap * (rows - 1)) / rows
        canvas.delete("all")
        for r in range(rows):
            for c in range(cols):
                x0 = pad + c * (cw + gap)
                y0 = pad + r * (ch + gap)
                canvas.create_rectangle(x0, y0, x0 + cw, y0 + ch, outline=ACCENT, fill="#F3E4E4", width=1)

    def _slider(self, parent, label: str, var: tk.DoubleVar, lo: float, hi: float, unit: str) -> tk.Label:
        row = tk.Frame(parent, bg=PAPER)
        row.pack(fill="x", pady=4)
        tk.Label(row, text=label, bg=PAPER, fg=INK, font=_font("Microsoft YaHei UI", 10), width=10, anchor="w").pack(side="left")
        readout = tk.Label(row, text="", bg=PAPER, fg=ACCENT, font=_font("Microsoft YaHei UI", 10, "bold"), width=8, anchor="e")
        readout.pack(side="right")
        scale = tk.Scale(
            parent,
            from_=lo,
            to=hi,
            resolution=0.05 if hi <= 1.01 else 0.1,
            orient="horizontal",
            variable=var,
            showvalue=0,
            bg=PAPER,
            fg=INK,
            troughcolor="#C8BFB3",
            highlightthickness=0,
            bd=0,
            sliderrelief="flat",
            activebackground=ACCENT,
            command=lambda _e: self._refresh(),
        )
        scale.pack(fill="x")
        readout._unit = unit  # type: ignore[attr-defined]
        readout._var = var  # type: ignore[attr-defined]
        return readout

    def _ghost_btn(self, parent, text, command) -> tk.Button:
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=WHITE,
            fg=INK,
            relief="flat",
            highlightthickness=1,
            highlightbackground=LINE,
            font=_font("Microsoft YaHei UI", 9),
            cursor="hand2",
            padx=10,
            pady=4,
        )

    def _opts(self) -> dict:
        return {
            "font_family": FONT_ARIAL,
            "axis_line_pt": round(float(self.axis_line.get()), 2),
            "tick_label_pt": round(float(self.tick_label.get()), 2),
        }

    def _open(self) -> None:
        path = filedialog.askopenfilename(
            title="选择已组好的图 JSON",
            filetypes=[("Figure JSON", "*.json"), ("All files", "*.*")],
        )
        if path:
            self.figure_path.set(path)
            self._refresh()

    def _refresh(self) -> None:
        for card in self._cards:
            card.refresh()
            for child in card.winfo_children():
                if isinstance(child, tk.Canvas):
                    self._draw_thumb(child, card.value)
        self.axis_readout.configure(text=f"{self.axis_line.get():.2f} pt")
        self.tick_readout.configure(text=f"{self.tick_label.get():.1f} pt")
        try:
            plan = plan_layout(self.column.get(), self.layout.get())
            graph = inspect_active_graph()
            if graph:
                match = graph["layers"] == plan.panel_count
                chip = (
                    f"当前 Origin 图  {graph['name']}  ·  {graph['layers']} 个图层\n"
                    + (
                        f"与「{plan.layout_name}」一致，可以直接套用。"
                        if match
                        else f"「{plan.layout_name}」需要 {plan.panel_count} 个图层。请改布局，或先在 Origin 里把图组好。"
                    )
                )
                self.status.configure(text=chip, bg="#E7F2EC" if match else "#F8EBD9", fg=OK if match else WARN)
            elif self.origin_mode:
                self.status.configure(
                    text="请先在 Origin 里打开并点选一张已经组好的图，再点套用。",
                    bg="#F8EBD9",
                    fg=WARN,
                )
            else:
                self.status.configure(
                    text=f"预览  {plan.page_width_mm:.0f} × {plan.page_height_mm:.0f} mm  ·  {plan.panel_count} 个面板。打开 Origin 图或 JSON 后即可套用。",
                    bg=CHIP,
                    fg=INK,
                )
            lines = [
                f"{plan.column_mode}  ·  {plan.layout_name}",
                f"页面  {plan.page_width_mm:.2f} × {plan.page_height_mm:.2f} mm",
                f"轴体 {self.axis_line.get():.2f} pt    轴上数字 {self.tick_label.get():.1f} pt",
                "",
            ]
            for box in plan.panels:
                lines.append(f"  {box.label}   {box.width_mm:.2f} × {box.height_mm:.2f} mm")
            self._set_preview("\n".join(lines))
        except NatureFormatError as exc:
            self._set_preview(str(exc))

    def _apply(self) -> None:
        column = self.column.get()
        layout = self.layout.get()
        opts = self._opts()
        try:
            from .origin_adapter import apply_to_active_origin

            if self.origin_mode or inspect_active_graph():
                text = apply_to_active_origin(column, layout, **opts)
                self._set_preview("已套用到当前 Origin 图。\n数据、标记和颜色没有改。\n\n" + text)
                self.status.configure(text="已套用 Nature 排版。请在 Origin 里看当前图。", bg="#E7F2EC", fg=OK)
                return
            path = self.figure_path.get().strip()
            if path:
                result = restyle_path(path, column, layout, **opts)
                out = Path(path).with_name(Path(path).stem + "_nature.json")
                dump_figure(result.figure, out)
                from .origin_adapter import labtalk_restyle_script

                labtalk = Path(path).with_name(Path(path).stem + "_nature.ogs")
                labtalk.write_text(
                    labtalk_restyle_script(
                        result.plan,
                        font_family=opts["font_family"],
                        axis_line_pt=opts["axis_line_pt"],
                        tick_label_pt=opts["tick_label_pt"],
                        tick_line_pt=opts["axis_line_pt"],
                    ),
                    encoding="utf-8",
                )
                self._set_preview(format_result(result) + f"\n已写出：\n  {out}\n  {labtalk}\n")
                return
            figure = assembled_figure(panel_count_for(layout))
            result = apply_nature_format(figure, column, layout, **opts)
            self._set_preview(format_result(result) + "\n还没有 Origin 图。打开 Origin 后点套用，或先打开 JSON。\n")
        except (NatureFormatError, PanelCountError, OriginUnavailableError) as exc:
            messagebox.showerror("无法套用", str(exc))
            self._set_preview(str(exc))
            self.status.configure(text=str(exc), bg="#F8EBD9", fg=WARN)

    def _set_preview(self, text: str) -> None:
        first = text.strip().splitlines()
        self.preview.configure(text="  ·  ".join(first[:3]))


def build_app(root: tk.Tk | None = None, *, origin_mode: bool = False) -> tk.Tk:
    _enable_dpi()
    if root is None:
        root = tk.Tk()
    NatureFormatApp(root, origin_mode=origin_mode)
    return root


def main(*, origin_mode: bool = False) -> None:
    root = build_app(origin_mode=origin_mode)
    root.mainloop()
