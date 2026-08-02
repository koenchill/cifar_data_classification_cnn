# Runbook — Critical and SLO Alert Response

| Alert | Sev | First actions | Escalate if |
|---|---|---|---|
| `CifarCnnApiReplicaShortage` | Critical | Check Deployment/HPA/PDB; node pressure; recent rollout digest | &lt;2 available &gt;5m → incident Sev-2/1 |
| `CifarCnnApiHighErrorRate` | Warning→page if sustained | Logs for 5xx; bundle ready; IdP; rollback digest if post-promote | Error SLO burned for hour |
| `CifarCnnApiHighLatency` | Warning | HPA, CPU throttle, cold start; capacity vs Phase 12 envelope | p95 &gt;500ms sustained |
| `CifarCnnApiAuthDeniesSpike` | Security | JWKS/issuer; client misconfig vs abuse; NetworkPolicy to IdP | Confirmed authz bypass → Sev-1 |
| Argo sync failed | Warning/Critical | App conditions; admission deny; Git drift | Prod OutOfSync &gt;15m |

## Proof standard (ORR)

Alert names and thresholds must match `deploy/kustomize/base/prometheusrule.yaml` and `docs/governance/slo_policy.md`. Routing to the on-call channel is an environment bootstrap step (Pager/Slack); logic is proven via rule presence + tabletop.
