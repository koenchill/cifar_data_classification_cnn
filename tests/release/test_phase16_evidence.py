"""Phase 16 release-candidate evidence presence and matrix sanity checks."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "docs" / "evidence" / "release-e"

REQUIRED = (
    "requirements_to_test_matrix.md",
    "verification_results.md",
    "verification_results.json",
    "defect_exception_register.md",
    "threat_model_review.md",
    "pen_test_tabletop.md",
    "ai_review.md",
    "game_day.md",
    "stakeholder_acceptance.md",
    "qa_signoff.md",
    "phase-16-gate.md",
)


@pytest.mark.parametrize("name", REQUIRED)
def test_phase16_evidence_file_exists(name: str) -> None:
    path = EVIDENCE / name
    assert path.is_file(), f"missing Phase 16 evidence: {path}"
    assert path.stat().st_size > 0


def test_verification_results_json_reports_pass() -> None:
    payload = json.loads((EVIDENCE / "verification_results.json").read_text(encoding="utf-8"))
    assert payload["exit_code"] == 0
    assert payload["pass_criteria"]["pytest_exit_zero"] is True
    assert payload["pass_criteria"]["flaky_gates_unexplained"] is False
    assert "passed" in payload["summary_line"].lower()
    assert "failed" not in payload["summary_line"].lower().split("passed")[0]
    assert "--ignore=tests/release" in payload["command"]


def test_matrix_covers_release_gates() -> None:
    text = (EVIDENCE / "requirements_to_test_matrix.md").read_text(encoding="utf-8")
    for token in ("A-GUIDE", "B-BUNDLE", "C-API", "D-GITOPS", "E-QA", "SEC-03"):
        assert token in text


def test_defect_register_has_no_open_critical() -> None:
    text = (EVIDENCE / "defect_exception_register.md").read_text(encoding="utf-8").lower()
    assert "no critical" in text or "none open critical" in text or "no open critical" in text
    assert "| critical |" not in text or "critical defects" in text


def test_qa_signoff_approved() -> None:
    text = (EVIDENCE / "qa_signoff.md").read_text(encoding="utf-8")
    assert "QA APPROVED" in text
