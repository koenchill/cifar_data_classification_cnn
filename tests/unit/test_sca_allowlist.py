"""Unit tests for SCA allowlist gate."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ALLOWLIST = ROOT / "security" / "sca-allowlist.txt"
SCRIPT = ROOT / "scripts" / "check_sca_allowlist.py"


def _load_mod():
    spec = importlib.util.spec_from_file_location("check_sca_allowlist", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_allowlist_file_non_empty() -> None:
    mod = _load_mod()
    ids = mod.load_allowlist(ALLOWLIST)
    assert len(ids) >= 1
    assert all(not i.startswith("#") for i in ids)


def test_findings_parser_and_gate(tmp_path: Path) -> None:
    mod = _load_mod()
    report = {
        "dependencies": [
            {
                "name": "demo",
                "version": "0.0.1",
                "vulns": [{"id": "PYSEC-TEST-1", "fix_versions": ["1.0.0"]}],
            }
        ]
    }
    path = tmp_path / "r.json"
    path.write_text(json.dumps(report), encoding="utf-8")
    assert mod.findings_from_pip_audit(report) == [("demo", "PYSEC-TEST-1", "1.0.0")]
    allow = tmp_path / "allow.txt"
    allow.write_text("PYSEC-TEST-1\n", encoding="utf-8")
    assert mod.main(["--report", str(path), "--allowlist", str(allow)]) == 0
    assert mod.main(["--report", str(path), "--allowlist", str(ALLOWLIST)]) == 1
