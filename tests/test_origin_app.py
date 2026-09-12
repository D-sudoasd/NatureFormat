"""Origin App packaging: gallery launch files and verbatim UI names."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "origin_app" / "NatureFormat"


def test_origin_app_launch_files_exist() -> None:
    assert (APP / "Launch.ogs").is_file()
    assert (APP / "open_app.py").is_file()
    assert (APP / "package.ini").is_file()
    launch = (APP / "Launch.ogs").read_text(encoding="utf-8")
    assert "open_app.py" in launch
    assert "run -pyf" in launch
    ini = (APP / "package.ini").read_text(encoding="utf-8")
    assert "Nature 一键排版" in ini
    assert "Graph=1" in ini
    assert "Launch.ogs" in ini


def test_open_app_uses_origin_mode() -> None:
    text = (APP / "open_app.py").read_text(encoding="utf-8")
    assert "origin_mode=True" in text
    assert "natureformat.ui" in text


def test_app_icon_png() -> None:
    icon = APP / "AppIcon.png"
    assert icon.is_file()
    data = icon.read_bytes()
    assert data.startswith(b"\x89PNG\r\n\x1a\n")
    assert icon.stat().st_size > 50
