"""Make ``tests/unit`` importable as a plain module path in all test layers."""

from __future__ import annotations

import sys
from pathlib import Path

_UNIT = Path(__file__).resolve().parent / "unit"
if str(_UNIT) not in sys.path:
    sys.path.insert(0, str(_UNIT))
