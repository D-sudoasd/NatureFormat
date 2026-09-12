"""Origin Apps Gallery entry. Runs inside Origin's embedded Python."""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
for candidate in (HERE, HERE.parent.parent):
    if (candidate / "natureformat" / "ui.py").exists():
        path = str(candidate)
        if path not in sys.path:
            sys.path.insert(0, path)
        break

from natureformat.ui import main  # noqa: E402


if __name__ == "__main__":
    main(origin_mode=True)
