#!/usr/bin/env python3
"""Fail CI when pip-audit findings are not covered by security/sca-allowlist.txt."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ALLOWLIST = ROOT / "security" / "sca-allowlist.txt"


def load_allowlist(path: Path) -> set[str]:
    ids: set[str] = set()
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        ids.add(line.split()[0])
    return ids


def findings_from_pip_audit(payload: object) -> list[tuple[str, str, str]]:
    """Return (package, vuln_id, fix_versions) tuples."""
    out: list[tuple[str, str, str]] = []
    if not isinstance(payload, dict):
        return out
    deps = payload.get("dependencies", [])
    if not isinstance(deps, list):
        return out
    for dep in deps:
        if not isinstance(dep, dict):
            continue
        name = str(dep.get("name", "unknown"))
        vulns = dep.get("vulns", [])
        if not isinstance(vulns, list):
            continue
        for vuln in vulns:
            if not isinstance(vuln, dict):
                continue
            vid = str(vuln.get("id") or vuln.get("alias") or "").strip()
            if not vid:
                continue
            fixes = vuln.get("fix_versions") or []
            fix_s = ",".join(str(x) for x in fixes) if isinstance(fixes, list) else str(fixes)
            out.append((name, vid, fix_s))
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, required=True, help="pip-audit JSON report")
    parser.add_argument("--allowlist", type=Path, default=DEFAULT_ALLOWLIST)
    args = parser.parse_args(argv)

    payload = json.loads(args.report.read_text(encoding="utf-8"))
    allow = load_allowlist(args.allowlist)
    findings = findings_from_pip_audit(payload)
    unexpected = [(pkg, vid, fix) for pkg, vid, fix in findings if vid not in allow]

    print(f"sca_findings={len(findings)} allowlisted={len(findings) - len(unexpected)}")
    if unexpected:
        print(
            "Unexpected SCA findings (allowlist only with risk acceptance):",
            file=sys.stderr,
        )
        for pkg, vid, fix in unexpected:
            print(f"  {pkg}: {vid} (fix: {fix or 'n/a'})", file=sys.stderr)
        return 1
    if not findings:
        print("No SCA findings from pip-audit.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
