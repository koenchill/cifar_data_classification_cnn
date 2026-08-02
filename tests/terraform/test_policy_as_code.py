"""Static policy-as-code gates for Terraform (no AWS credentials required)."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TF_ROOT = ROOT / "infra" / "terraform"


def _tf_files() -> list[Path]:
    return [p for p in TF_ROOT.rglob("*.tf") if ".terraform" not in p.parts]


def test_no_administrator_access_managed_policy() -> None:
    pattern = re.compile(r"arn:aws:iam::aws:policy/AdministratorAccess")
    offenders = [str(p) for p in _tf_files() if pattern.search(p.read_text(encoding="utf-8"))]
    assert offenders == [], f"AdministratorAccess forbidden: {offenders}"


def test_no_iam_action_star_allow() -> None:
    """Reject Allow statements that use Action = \"*\" in inline JSON policies."""
    # Match Effect Allow followed closely by Action "*"
    allow_star = re.compile(
        r'"Effect"\s*:\s*"Allow"[\s\S]{0,200}"Action"\s*:\s*"\*"',
        re.MULTILINE,
    )
    offenders: list[str] = []
    for path in _tf_files():
        text = path.read_text(encoding="utf-8")
        if allow_star.search(text):
            offenders.append(str(path.relative_to(ROOT)))
    assert offenders == [], f"Wildcard Allow Action forbidden: {offenders}"


def test_security_group_has_no_open_ingress() -> None:
    ingress_open = re.compile(
        r"ingress\s*\{[^}]*cidr_blocks\s*=\s*\[[^\]]*0\.0\.0\.0/0",
        re.DOTALL,
    )
    offenders: list[str] = []
    for path in _tf_files():
        text = path.read_text(encoding="utf-8")
        if ingress_open.search(text):
            offenders.append(str(path.relative_to(ROOT)))
    assert offenders == [], f"Open SG ingress forbidden: {offenders}"


def test_ecr_immutable_and_scan() -> None:
    ecr = (TF_ROOT / "modules" / "ecr" / "main.tf").read_text(encoding="utf-8")
    assert 'image_tag_mutability = "IMMUTABLE"' in ecr
    assert "scan_on_push = true" in ecr
    assert 'encryption_type = "KMS"' in ecr


def test_eks_secrets_encryption_and_private_nodes() -> None:
    eks = (TF_ROOT / "modules" / "eks" / "main.tf").read_text(encoding="utf-8")
    assert 'resources = ["secrets"]' in eks
    assert "subnet_ids      = var.private_subnet_ids" in eks
    staging = (TF_ROOT / "envs" / "staging" / "variables.tf").read_text(encoding="utf-8")
    assert "endpoint_public_access" in staging


def test_state_keys_are_per_environment() -> None:
    for env in ("dev", "staging", "prod"):
        backend = (TF_ROOT / "envs" / env / "backend.hcl.example").read_text(encoding="utf-8")
        assert f"envs/{env}/terraform.tfstate" in backend


def test_ci_build_cannot_update_eks_cluster() -> None:
    iam = (TF_ROOT / "modules" / "iam_github_oidc" / "main.tf").read_text(encoding="utf-8")
    assert "DenyTerraformApplySurfaces" in iam
    assert "eks:UpdateClusterConfig" in iam
    assert "ci-build" in iam
