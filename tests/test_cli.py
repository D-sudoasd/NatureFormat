"""Gating: real entry point python -m natureformat, twice, must match."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "assembled_six_panel.json"


def _run(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "natureformat", *args],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
    )


def test_apply_single_column_six_grid_twice_matches() -> None:
    args = ["apply", "--column", "单栏", "--layout", "六宫格", str(EXAMPLE)]
    first = _run(args)
    second = _run(args)
    assert first.returncode == 0, first.stderr
    assert second.returncode == 0, second.stderr
    assert first.stdout == second.stdout
    assert "page_width_mm: 89.00" in first.stdout
    assert "layout: 六宫格" in first.stdout
    assert "column_mode: 单栏（Single Column）" in first.stdout
    assert "panel_count: 6" in first.stdout
    for label in "abcdef":
        assert f"panel {label}:" in first.stdout
        assert "width_mm=" in first.stdout
        assert "height_mm=" in first.stdout


def test_help_lists_verbatim_names() -> None:
    help_text = _run(["--help"]).stdout
    for name in (
        "单栏（Single Column）",
        "双栏（Double Column）",
        "单图（一行一图）",
        "两图一行",
        "三图一行",
        "六宫格",
        "九宫格",
    ):
        assert name in help_text


def test_mismatch_exits_nonzero() -> None:
    proc = _run(["apply", "--column", "双栏", "--layout", "九宫格", str(EXAMPLE)])
    assert proc.returncode == 2
    assert "需要 9" in proc.stderr
    assert "不会丢弃" in proc.stderr
