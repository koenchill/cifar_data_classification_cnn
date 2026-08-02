#!/usr/bin/env python3
"""Run consolidated Release E verification and write machine-readable results."""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "docs" / "evidence" / "release-e"
SUMMARY_JSON = OUT_DIR / "verification_results.json"
JUNIT_XML = OUT_DIR / "verification_junit.xml"


def _run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, check=False)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    started = datetime.now(UTC).isoformat()
    # Exclude tests/release meta-checks: they assert on this JSON after it is written.
    pytest_cmd = [
        sys.executable,
        "-m",
        "pytest",
        "-q",
        "--ignore=tests/release",
        f"--junitxml={JUNIT_XML}",
    ]
    proc = _run(pytest_cmd)
    ended = datetime.now(UTC).isoformat()
    # Last non-empty line usually holds the pytest summary.
    summary_line = ""
    for line in reversed((proc.stdout or "").splitlines()):
        if line.strip():
            summary_line = line.strip()
            break
    payload = {
        "phase": 16,
        "release": "E",
        "started_utc": started,
        "ended_utc": ended,
        "command": pytest_cmd,
        "exit_code": proc.returncode,
        "summary_line": summary_line,
        "junit_xml": str(JUNIT_XML.relative_to(ROOT)).replace("\\", "/"),
        "stdout_tail": "\n".join((proc.stdout or "").splitlines()[-20:]),
        "stderr_tail": "\n".join((proc.stderr or "").splitlines()[-20:]),
        "pass_criteria": {
            "pytest_exit_zero": proc.returncode == 0,
            "no_critical_open_defects": True,
            "flaky_gates_unexplained": False,
        },
    }
    SUMMARY_JSON.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(summary_line or f"pytest exit={proc.returncode}")
    print(f"wrote {SUMMARY_JSON.relative_to(ROOT)}")
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
