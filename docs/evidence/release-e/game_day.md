# Resilience Game Day (Tabletop) — Phase 16

| Field | Value |
|---|---|
| Date | 2026-08-02 |
| Scope | API + K8s + GitOps failure modes |
| Refs | `docs/runbooks/k8s-*.md`, `docs/runbooks/gitops-*.md`, Phase 14 HA tabletop |

## Injects

| Inject | Expected response | Abort criteria | Desk result |
|---|---|---|---|
| Bad digest promoted to staging | Revert PR; Argo self-heal; no kubectl set image | Sync loop > retry budget | Covered by gitops-rollback runbook |
| Node drain / replica loss | PDB + topology; HPA; available ≥ 2 | Available < 2 for >5m | Phase 14 HA tabletop |
| Auth denial spike | Alert `CifarCnnApiAuthDeniesSpike`; check IdP/JWKS | Sustained unexplained spike | Observability runbook |
| Unsigned image push attempt | Kyverno Enforce reject | Policy disabled | Admission policies + tests |
| Bundle HMAC mismatch at boot | `/ready` fail closed; no predict | Serving with invalid bundle | Bundle + API fail-closed tests |

## Decision

Game day **pass** as tabletop. Live injects deferred with `DEF-16-01` until cluster bootstrap.
