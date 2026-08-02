"""Argo CD GitOps policy, promotion, and admission contract tests."""

from __future__ import annotations

import subprocess
import textwrap
from pathlib import Path
from typing import Any

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
ARGOCD = ROOT / "deploy" / "argocd"
PROMOTE_WF = ROOT / ".github" / "workflows" / "gitops-promote.yml"
PROMOTE_SCRIPT = ARGOCD / "scripts" / "propose_digest_promotion.py"
PROD_OVERLAY = ROOT / "deploy" / "kustomize" / "overlays" / "prod" / "kustomization.yaml"


def _load_docs(path: Path) -> list[dict[str, Any]]:
    docs = list(yaml.safe_load_all(path.read_text(encoding="utf-8")))
    return [d for d in docs if isinstance(d, dict)]


def _render_argocd() -> list[dict[str, Any]]:
    proc = subprocess.run(
        ["kubectl", "kustomize", str(ARGOCD)],
        check=True,
        capture_output=True,
        text=True,
    )
    docs = list(yaml.safe_load_all(proc.stdout))
    return [d for d in docs if isinstance(d, dict)]


@pytest.fixture(scope="module")
def argocd_docs() -> list[dict[str, Any]]:
    return _render_argocd()


def _by_kind(docs: list[dict[str, Any]], kind: str) -> list[dict[str, Any]]:
    return [d for d in docs if d.get("kind") == kind]


def test_appproject_denies_exec_override_delete(argocd_docs: list[dict[str, Any]]) -> None:
    project = next(d for d in _by_kind(argocd_docs, "AppProject") if d["metadata"]["name"] == "cifar-cnn")
    assert project["spec"]["sourceRepos"] == [
        "https://github.com/koenchill/cifar_data_classification_cnn.git"
    ]
    assert project["spec"]["clusterResourceWhitelist"] == []
    policy_blob = "\n".join(
        p for role in project["spec"]["roles"] for p in role.get("policies", [])
    )
    assert "applications, action/*, cifar-cnn/*, deny" in policy_blob
    assert "applications, delete, cifar-cnn/*, deny" in policy_blob
    assert "applications, override, cifar-cnn/*, deny" in policy_blob


def test_applications_prune_self_heal_and_isolation(argocd_docs: list[dict[str, Any]]) -> None:
    apps = {a["metadata"]["name"]: a for a in _by_kind(argocd_docs, "Application")}
    assert set(apps) >= {"cifar-cnn-dev", "cifar-cnn-staging", "cifar-cnn-prod"}
    for name, app in apps.items():
        assert app["spec"]["project"] == "cifar-cnn"
        assert app["spec"]["source"]["path"].startswith("deploy/kustomize/overlays/")
        auto = app["spec"]["syncPolicy"]["automated"]
        assert auto["prune"] is True
        assert auto["selfHeal"] is True
        assert app["spec"]["destination"]["namespace"] == "cifar-cnn"
    assert apps["cifar-cnn-staging"]["spec"]["source"]["path"].endswith("/staging")
    assert apps["cifar-cnn-prod"]["spec"]["source"]["path"].endswith("/prod")


def test_rbac_denies_exec_globally(argocd_docs: list[dict[str, Any]]) -> None:
    cm = next(d for d in _by_kind(argocd_docs, "ConfigMap") if d["metadata"]["name"] == "argocd-rbac-cm")
    csv = cm["data"]["policy.csv"]
    assert "exec, create, */*, deny" in csv
    assert "applications, override, */*, deny" in csv
    assert "applications, delete, */*, deny" in csv


def test_oidc_sso_configured_without_embedded_secrets(argocd_docs: list[dict[str, Any]]) -> None:
    cm = next(d for d in _by_kind(argocd_docs, "ConfigMap") if d["metadata"]["name"] == "argocd-cm")
    assert "oidc.config" in cm["data"]
    assert "$oidc.clientSecret" in cm["data"]["oidc.config"]
    blob = yaml.dump(cm)
    assert "BEGIN PRIVATE KEY" not in blob
    assert "client_secret:" not in blob.lower() or "$oidc" in blob


def test_admission_requires_digest_and_signatures(argocd_docs: list[dict[str, Any]]) -> None:
    policies = {p["metadata"]["name"]: p for p in _by_kind(argocd_docs, "ClusterPolicy")}
    digest = policies["cifar-cnn-require-image-digest"]
    signed = policies["cifar-cnn-verify-signed-images"]
    assert digest["spec"]["validationFailureAction"] == "Enforce"
    assert signed["spec"]["validationFailureAction"] == "Enforce"
    assert any("verifyImages" in r for r in signed["spec"]["rules"])
    pattern = digest["spec"]["rules"][0]["validate"]["pattern"]
    assert "@sha256:" in yaml.dump(pattern)


def test_prod_overlay_digest_pinned() -> None:
    text = PROD_OVERLAY.read_text(encoding="utf-8")
    assert "digest: sha256:" in text
    assert ":latest" not in text


def test_gitops_promote_workflow_never_applies_cluster() -> None:
    wf = yaml.safe_load(PROMOTE_WF.read_text(encoding="utf-8"))
    assert wf["permissions"].get("id-token") in (None, "none")
    text = PROMOTE_WF.read_text(encoding="utf-8")
    assert "kubectl apply" not in text
    assert "kubectl delete" not in text
    assert "helm upgrade" not in text
    assert "terraform apply" not in text
    assert "environment: gitops-prod" in text
    jobs = wf["jobs"]
    assert "promote-prod" in jobs
    assert jobs["promote-prod"]["environment"] == "gitops-prod"


def test_digest_promotion_script_updates_overlay(tmp_path: Path) -> None:
    import importlib.util

    overlay_dir = tmp_path / "deploy" / "kustomize" / "overlays" / "staging"
    overlay_dir.mkdir(parents=True)
    sample = textwrap.dedent(
        """\
        apiVersion: kustomize.config.k8s.io/v1beta1
        kind: Kustomization
        images:
          - name: ghcr.io/koenchill/cifar_data_classification_cnn/api
            newName: ghcr.io/koenchill/cifar_data_classification_cnn/api
            digest: sha256:6f43777bf8ad41ffaf3bf16645438463ebe36653b6453252e6bb7166101004c1
        """
    )
    (overlay_dir / "kustomization.yaml").write_text(sample, encoding="utf-8")
    spec = importlib.util.spec_from_file_location("propose_digest_promotion", PROMOTE_SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.ROOT = tmp_path
    mod.OVERLAY_ROOT = tmp_path / "deploy" / "kustomize" / "overlays"
    new_digest = "sha256:" + ("ab" * 32)
    path = mod.update_overlay("staging", new_digest)
    assert new_digest in path.read_text(encoding="utf-8")


def test_rollback_is_git_revert_not_ci_apply() -> None:
    runbook = (ROOT / "docs" / "runbooks" / "gitops-rollback.md").read_text(encoding="utf-8")
    lower = runbook.lower()
    assert "git revert" in lower or "reverts the promotion" in lower
    assert "not" in lower and "kubectl apply" in lower
    assert "self-heal" in lower
