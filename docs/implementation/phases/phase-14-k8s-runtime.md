# Phase 14 — Hardened Kubernetes Runtime, Network Policies, Capacity, and Observability

| Field | Value |
|---|---|
| Release | D |
| Depends | Phase 13 |
| Status | `todo` |
| Evidence | `docs/evidence/release-d/phase-14-gate.md` |

## Objective

Deploy the signed artifact under enforced workload, network, availability, and capacity controls.

## Allowed paths

- `deploy/kustomize/`
- `docs/runbooks/`
- `docs/evidence/release-d/`
- `tests/`

## Forbidden

- Privileged/hostPath/host namespaces/unsafe capabilities
- Default-allow egress in app namespaces
- Guessed requests/limits replacing Phase 12 measurements

## Workstreams

### Policy + network + secrets

  - [ ] Restricted PSS; default-deny NetworkPolicies; External Secrets; tight RBAC

### Availability + capacity

  - [ ] >=2 replicas; topology; PDB; probes; measured requests/limits; HPA; pool separation

### Observability

  - [ ] Logs/metrics/traces; dashboards/alerts for SLOs and security/ops signals

## Deliverables

- `Kustomize base/overlays; policies; quotas; probes; HPA/PDB; secrets; dashboards`
- `docs/evidence/release-d/phase-14-gate.md`

## Exit gate

- [ ] Policy/manifest and network positive/negative tests pass
- [ ] Scale/rollout/eviction/node-loss tests pass without unacceptable interruption

## Verify

```text
kubectl kustomize deploy/kustomize/overlays/staging
pytest -q tests/integration -k k8s_policy
```

## Cursor prompt (copy)

```text
Execute Phase 14 only per docs/implementation/phases/phase-14-k8s-runtime.md.
Respect Allowed paths and Forbidden paths.
Complete workstreams in order; check off tasks as done.
Write exit-gate evidence to docs/evidence/release-d/phase-14-gate.md.
Do not start the next phase.
```

## Done when

- [ ] All workstream tasks complete
- [ ] Deliverables exist at listed paths
- [ ] Exit gate criteria satisfied
- [ ] Verify commands recorded/pass
- [ ] No global stop condition triggered
