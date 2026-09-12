"""Origin App launch target: apply 单栏 + 六宫格 to the active graph if possible."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from natureformat.origin_adapter import apply_to_active_origin  # noqa: E402


def main() -> None:
    try:
        text = apply_to_active_origin("单栏（Single Column）", "六宫格")
        print(text)
    except Exception as exc:
        print(exc)
        raise SystemExit(2) from exc


if __name__ == "__main__":
    main()
