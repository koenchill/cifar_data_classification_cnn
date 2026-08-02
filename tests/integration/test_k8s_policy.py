"""Positive/negative policy tests for hardened Kustomize manifests."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
STAGING = ROOT / "deploy" / "kustomize" / "overlays" / "staging"


def _render(overlay: Path) -> list[dict[str, Any]]:
    proc = subprocess.run(
        ["kubectl", "kustomize", str(overlay)],
        check=True,
        capture_output=True,
        text=True,
    )
    docs = list(yaml.safe_load_all(proc.stdout))
    return [d for d in docs if isinstance(d, dict)]


@pytest.fixture(scope="module")
def staging_docs() -> list[dict[str, Any]]:
    return _render(STAGING)


def _by_kind(docs: list[dict[str, Any]], kind: str) -> list[dict[str, Any]]:
    return [d for d in docs if d.get("kind") == kind]


def test_k8s_policy_namespace_restricted_pss(staging_docs: list[dict[str, Any]]) -> None:
    ns = _by_kind(staging_docs, "Namespace")[0]
    labels = ns["metadata"]["labels"]
    assert labels["pod-security.kubernetes.io/enforce"] == "restricted"


def test_k8s_policy_default_deny_network(staging_docs: list[dict[str, Any]]) -> None:
    policies = _by_kind(staging_docs, "NetworkPolicy")
    names = {p["metadata"]["name"] for p in policies}
    assert "default-deny-all" in names
    deny = next(p for p in policies if p["metadata"]["name"] == "default-deny-all")
    assert set(deny["spec"]["policyTypes"]) == {"Ingress", "Egress"}
    assert deny["spec"].get("ingress") in (None, [])
    assert deny["spec"].get("egress") in (None, [])


def test_k8s_policy_no_privileged_or_hostpath(staging_docs: list[dict[str, Any]]) -> None:
    dep = _by_kind(staging_docs, "Deployment")[0]
    pod = dep["spec"]["template"]["spec"]
    assert pod.get("hostNetwork") is False
    assert pod.get("hostPID") is False
    assert pod.get("hostIPC") is False
    for vol in pod.get("volumes", []):
        assert "hostPath" not in vol
    for c in pod["containers"]:
        sc = c["securityContext"]
        assert sc.get("privileged") is not True
        assert sc.get("allowPrivilegeEscalation") is False
        assert sc.get("readOnlyRootFilesystem") is True
        assert "ALL" in sc.get("capabilities", {}).get("drop", [])


def test_k8s_policy_ha_capacity_from_phase12(staging_docs: list[dict[str, Any]]) -> None:
    dep = _by_kind(staging_docs, "Deployment")[0]
    assert dep["spec"]["replicas"] >= 2
    resources = dep["spec"]["template"]["spec"]["containers"][0]["resources"]
    assert resources["requests"]["cpu"] == "250m"
    assert resources["requests"]["memory"] == "512Mi"
    assert resources["limits"]["memory"] == "2Gi"
    hpa = _by_kind(staging_docs, "HorizontalPodAutoscaler")[0]
    assert hpa["spec"]["minReplicas"] >= 2
    pdb = _by_kind(staging_docs, "PodDisruptionBudget")[0]
    assert pdb["spec"]["minAvailable"] >= 1


def test_k8s_policy_image_pinned_by_digest(staging_docs: list[dict[str, Any]]) -> None:
    dep = _by_kind(staging_docs, "Deployment")[0]
    image = dep["spec"]["template"]["spec"]["containers"][0]["image"]
    assert "@sha256:" in image
    assert ":latest" not in image


def test_k8s_policy_external_secret_present(staging_docs: list[dict[str, Any]]) -> None:
    kinds = {d["kind"] for d in staging_docs}
    assert "ExternalSecret" in kinds
    assert "SecretStore" in kinds


def test_k8s_policy_observability_assets(staging_docs: list[dict[str, Any]]) -> None:
    kinds = {d["kind"] for d in staging_docs}
    assert "PrometheusRule" in kinds
    cms = _by_kind(staging_docs, "ConfigMap")
    names = {c["metadata"]["name"] for c in cms}
    assert "grafana-dashboard-cifar-cnn-api" in names
    assert "api-observability" in names


def test_k8s_policy_negative_no_cluster_admin_binding(staging_docs: list[dict[str, Any]]) -> None:
    for d in staging_docs:
        if d.get("kind") not in {"RoleBinding", "ClusterRoleBinding"}:
            continue
        ref = d.get("roleRef", {})
        assert ref.get("name") != "cluster-admin"
        assert d.get("kind") != "ClusterRoleBinding"
