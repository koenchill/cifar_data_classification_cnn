#!/usr/bin/env python3
"""Static verification of Dockerfile/compose hardening controls."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCKERFILE = ROOT / "deploy" / "docker" / "Dockerfile"
COMPOSE = ROOT / "deploy" / "docker" / "compose.yaml"


def check_dockerfile(text: str) -> list[str]:
    errors: list[str] = []
    if "FROM ${PYTHON_BASE}" not in text and "FROM python@" not in text:
        pinned = re.search(r"FROM\s+python@sha256:", text) or (
            "PYTHON_BASE=python@sha256:" in text
        )
        if not pinned:
            errors.append("base image must be pinned by digest")
    if "USER 10001:10001" not in text and "USER 10001" not in text:
        errors.append("non-root USER 10001 required")
    if "AS builder" not in text or "AS runtime" not in text:
        errors.append("multi-stage builder/runtime required")
    forbidden_markers = ("gcc ", "apt-get install", "datasets", "train.py")
    runtime_section = text.split("AS runtime", 1)[-1]
    for marker in forbidden_markers:
        if marker in runtime_section:
            errors.append(f"runtime stage must not contain {marker!r}")
    if "MODEL_BUNDLE_PATH" not in text:
        errors.append("model preload path MODEL_BUNDLE_PATH required")
    return errors


def check_compose(text: str) -> list[str]:
    errors: list[str] = []
    for required in (
        "read_only: true",
        "no-new-privileges:true",
        "cap_drop:",
        'user: "10001:10001"',
    ):
        if required not in text:
            errors.append(f"compose missing {required!r}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    errors = check_dockerfile(DOCKERFILE.read_text(encoding="utf-8"))
    errors.extend(check_compose(COMPOSE.read_text(encoding="utf-8")))
    if errors:
        print("FAIL:", file=sys.stderr)
        for err in errors:
            print(f" - {err}", file=sys.stderr)
        return 1
    print("OK: docker envelope hardening checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
