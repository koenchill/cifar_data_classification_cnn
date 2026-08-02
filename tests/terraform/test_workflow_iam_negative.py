"""Negative trust assertions for Terraform CI workflows."""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
WF = ROOT / ".github" / "workflows"


def _load(name: str) -> dict:
    return yaml.safe_load((WF / name).read_text(encoding="utf-8"))


def test_ci_pr_still_blocks_oidc_apply() -> None:
    doc = _load("ci-pr.yml")
    assert doc["permissions"]["id-token"] == "none"
    assert doc["permissions"]["contents"] == "read"


def test_terraform_workflow_has_no_static_aws_keys() -> None:
    text = (WF / "terraform.yml").read_text(encoding="utf-8")
    assert "AWS_ACCESS_KEY_ID" not in text
    assert "AWS_SECRET_ACCESS_KEY" not in text


def test_terraform_workflow_default_job_denies_id_token() -> None:
    doc = _load("terraform.yml")
    job = doc["jobs"]["fmt-validate-policy"]
    assert job["permissions"]["id-token"] == "none"


def test_optional_plan_uses_oidc_not_apply() -> None:
    text = (WF / "terraform.yml").read_text(encoding="utf-8")
    assert "configure-aws-credentials" in text
    assert "role-to-assume" in text
    assert "terraform plan" in text
    assert "terraform apply" not in text


def test_terraform_fmt_validate_commands_present() -> None:
    text = (WF / "terraform.yml").read_text(encoding="utf-8")
    assert "fmt -check" in text
    assert "validate" in text
    assert "init -backend=false" in text
