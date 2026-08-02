# Phase 14 Gate — Hardened Kubernetes Runtime

| Field | Value |
|---|---|
| Phase | 14 — K8s runtime / network / capacity / observability |
| Release | D |
| Date | 2026-08-01 |
| Status | Pass (manifest + policy tests; cluster soak deferred to live EKS) |

## Exit criteria

- [x] Restricted PSS; default-deny NetworkPolicies; External Secrets; tight RBAC
- [x] ≥2 replicas; topology spread; PDB; probes; Phase-12 requests/limits; HPA; inference pool separation
- [x] Logs/metrics/traces hooks; Grafana dashboard ConfigMap; PrometheusRule SLO/security alerts
- [x] Policy/manifest positive/negative tests (`tests/integration/test_k8s_policy.py`)
- [x] Scale/rollout/eviction procedures documented (runbooks); tabletop expectations recorded

## Deliverables

| Artifact | Path |
|---|---|
| Kustomize base | `deploy/kustomize/base/` |
| Overlays | `deploy/kustomize/overlays/{dev,staging,prod}/` |
| Runbooks | `docs/runbooks/k8s-*.md` |
| Policy tests | `tests/integration/test_k8s_policy.py` |
| HA tabletop | `docs/evidence/release-d/phase-14-ha-tabletop.md` |

## Verify

```text
kubectl kustomize deploy/kustomize/overlays/staging
pytest -q tests/integration -k k8s_policy
```

Local result (2026-08-01): **8 passed**.

## Notes

- Live drain/node-loss soak requires Phase 13 cluster apply; runbooks define abort criteria.
- Image digests in overlays must be replaced with signed GHCR digests from `ci-image` before prod promotion.
