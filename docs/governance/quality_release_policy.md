# Quality and Release Policy

## Committed security controls (attachment)

These are mandatory for production application release (Release C+), not backlog:

1. No secrets in source  
2. Secure environment configuration (fail closed on missing security settings)  
3. Authentication  
4. OAuth / OIDC  
5. Strict rate limiting  
6. RBAC (deny by default)  
7. Comprehensive audit logging (no image bytes, tokens, or secrets)

## Release thresholds (initial candidates)

| Gate | Threshold |
|---|---|
| Guide baseline (A) | All `GUIDE_TRACEABILITY.md` rows done; model save/load works |
| Model promotion (B) | Predeclared champion rule; no test leakage; bundle hash/sign; AI risks owned |
| App release (C) | OIDC/RBAC/rate/audit suites green; critical vulns remediated or accepted |
| Platform (D) | Terraform/policy gates; network positive/negative; Argo promotion trace |
| Production (E) | ORR signed; rollback proven; residual risks accepted by named authority |

## SLO candidates (to approve in Phase 17)

| SLI | Candidate SLO |
|---|---|
| Availability (`/ready`) | ≥ 99.5% monthly (staging may be lower) |
| Predict latency (p95, warm, allowed image size) | ≤ 500 ms on measured envelope (revise from Phase 12 benches) |
| Error rate (5xx) | ≤ 1% under target load |
| Auth failure alert | Page on sustained spike |

## Severity taxonomy

| Severity | Definition | Response |
|---|---|---|
| Critical | Active exploit, secret leak, unsigned prod deploy, safety-prohibited misuse enabled | Stop promote; immediate remediation |
| High | Authz bypass, high AI risk unaccepted, SLO burn severe | Block release; fix or formal accept ≤ 30d |
| Medium | Material defect with workaround | Fix in next release train |
| Low | Minor / cosmetic | Backlog |

## Defect policy

- No known Critical in release candidate.  
- High requires fix or formal acceptance (owner, compensating control, expiry).  
- Flaky gates are defects; they cannot remain unexplained on an RC.

## Evidence retention

| Artifact | Retention |
|---|---|
| Phase gate files under `docs/evidence/` | Life of repo + 1 year after retirement |
| Training run records / metrics | ≥ 1 year for released models |
| SBOM / signatures / promotion traces | ≥ 1 year after release superseded |
| Audit logs (runtime) | Per platform policy (candidate ≥ 90 days) |

## Change and approval model

1. Changes via PR to `dev` (or feature branches → `dev`).  
2. Protected `main` / release branches; required reviews + status checks (Phase 1).  
3. Model-affecting data/split/config changes require model + data owner review.  
4. Infra/GitOps/security paths require CODEOWNERS review.  
5. Production promotion only through Argo CD from immutable signed digest after approval.
