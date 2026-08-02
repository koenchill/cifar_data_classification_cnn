"""Static checks for Phase 12 Docker envelope hardening."""

from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _load_verify_module():
    path = ROOT / "scripts" / "verify_image_envelope.py"
    spec = importlib.util.spec_from_file_location("verify_image_envelope", path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_dockerfile_hardening_markers() -> None:
    mod = _load_verify_module()
    text = (ROOT / "deploy" / "docker" / "Dockerfile").read_text(encoding="utf-8")
    assert mod.check_dockerfile(text) == []


def test_compose_security_envelope() -> None:
    mod = _load_verify_module()
    text = (ROOT / "deploy" / "docker" / "compose.yaml").read_text(encoding="utf-8")
    assert mod.check_compose(text) == []


def test_dockerignore_excludes_dataset_and_training() -> None:
    text = (ROOT / "deploy" / "docker" / "dockerignore").read_text(encoding="utf-8")
    assert "data" in text
    assert "artifacts" in text
    assert "scripts" in text
