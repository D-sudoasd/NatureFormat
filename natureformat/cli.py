"""Command-line entry. Same planner/apply as the one-click UI."""

from __future__ import annotations

import argparse
import sys

from .apply import apply_nature_format
from .demo import assembled_figure
from .errors import NatureFormatError
from .figure import dump_figure, load_figure
from .layouts import (
    COLUMN_SINGLE,
    LAYOUT_SIX,
    panel_count_for,
    plan_layout,
)
from .report import format_plan, format_result
from .spec import (
    DEFAULT_AXIS_LINE_PT,
    DEFAULT_TICK_LABEL_PT,
    FONT_ARIAL,
    FONT_HELVETICA,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="natureformat",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="一键把已组好的图改成 Nature 发表级排版（只改尺寸和字体，不改数据、标记、颜色）。",
        epilog=(
            "栏宽:\n"
            "  单栏（Single Column）\n"
            "  双栏（Double Column）\n"
            "布局:\n"
            "  单图（一行一图）\n"
            "  两图一行\n"
            "  三图一行\n"
            "  六宫格\n"
            "  九宫格"
        ),
    )
    sub = parser.add_subparsers(dest="command")

    apply_p = sub.add_parser("apply", help="套用 Nature 排版到已组好的图 JSON")
    _add_column_layout(apply_p)
    apply_p.add_argument(
        "--input",
        "-i",
        dest="input_path",
        default=None,
        help="已组好的图 JSON",
    )
    apply_p.add_argument(
        "input_positional",
        nargs="?",
        default=None,
        help="已组好的图 JSON（位置参数，与 --input 等价）",
    )
    apply_p.add_argument("--output", "-o", default=None, help="写出套用后的 JSON")
    apply_p.add_argument("--demo", action="store_true", help="使用内置示例（面板数随布局）")
    apply_p.add_argument("--font", choices=(FONT_ARIAL, FONT_HELVETICA), default=FONT_ARIAL)
    apply_p.add_argument("--axis-line", type=float, default=DEFAULT_AXIS_LINE_PT, help="轴体线宽 pt（0.25–1）")
    apply_p.add_argument("--tick-label", type=float, default=DEFAULT_TICK_LABEL_PT, help="轴上数字 pt（5–7）")
    apply_p.add_argument("--tick-line", type=float, default=None, help="刻度线宽 pt（默认与轴体相同）")

    plan_p = sub.add_parser("plan", help="只打印页面和各面板尺寸，不读图")
    _add_column_layout(plan_p)

    sub.add_parser("ui", help="打开一键排版窗口")

    origin_p = sub.add_parser("origin", help="尝试把排版应用到当前 Origin 图")
    _add_column_layout(origin_p)
    origin_p.add_argument("--axis-line", type=float, default=DEFAULT_AXIS_LINE_PT)
    origin_p.add_argument("--tick-label", type=float, default=DEFAULT_TICK_LABEL_PT)
    return parser


def _add_column_layout(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--column",
        "-c",
        default=COLUMN_SINGLE,
        help="单栏（Single Column）或 双栏（Double Column）",
    )
    parser.add_argument(
        "--layout",
        "-l",
        default=LAYOUT_SIX,
        help="单图（一行一图） / 两图一行 / 三图一行 / 六宫格 / 九宫格",
    )


def _load_input(args: argparse.Namespace):
    path = getattr(args, "input_path", None) or getattr(args, "input_positional", None)
    if path:
        return load_figure(path), path
    if getattr(args, "demo", False):
        return assembled_figure(panel_count_for(args.layout)), None
    return None, None


def cmd_plan(args: argparse.Namespace) -> int:
    plan = plan_layout(args.column, args.layout)
    sys.stdout.write(format_plan(plan) + "\n")
    return 0


def cmd_apply(args: argparse.Namespace) -> int:
    figure, _source = _load_input(args)
    if figure is None:
        raise NatureFormatError("请提供已组好的图 JSON（--input）或使用 --demo")
    result = apply_nature_format(
        figure,
        args.column,
        args.layout,
        font_family=getattr(args, "font", FONT_ARIAL),
        axis_line_pt=args.axis_line,
        tick_label_pt=args.tick_label,
        tick_line_pt=getattr(args, "tick_line", None),
    )
    sys.stdout.write(format_result(result) + "\n")
    if getattr(args, "output", None):
        dump_figure(result.figure, args.output)
    return 0


def cmd_ui(_args: argparse.Namespace) -> int:
    from .ui import main as ui_main

    ui_main()
    return 0


def cmd_origin(args: argparse.Namespace) -> int:
    from .origin_adapter import apply_to_active_origin

    text = apply_to_active_origin(
        args.column,
        args.layout,
        axis_line_pt=args.axis_line,
        tick_label_pt=args.tick_label,
    )
    sys.stdout.write(text + "\n")
    return 0


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    parser = _parser()
    if not argv:
        return cmd_ui(argparse.Namespace())
    args = parser.parse_args(argv)
    command = args.command
    try:
        if command == "plan":
            return cmd_plan(args)
        if command == "apply":
            return cmd_apply(args)
        if command == "ui":
            return cmd_ui(args)
        if command == "origin":
            return cmd_origin(args)
        parser.print_help()
        return 0
    except NatureFormatError as exc:
        sys.stderr.write(str(exc) + "\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
