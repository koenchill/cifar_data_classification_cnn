# AI and Cyber Risk Register

| Field | Value |
|---|---|
| Likelihood scale | 1 Rare – 5 Almost certain |
| Impact scale | 1 Negligible – 5 Severe |
| Score | Likelihood × Impact |
| Status values | open / treating / accepted / closed |

## Exception process

1. Requestor files risk ID, justification, compensating control, expiry (≤ 90 days default).  
2. Security owner + relevant domain owner review.  
3. AI system owner (AI risks) or security owner (cyber) records acceptance.  
4. Expired exceptions reopen as **open** and block related promotion gates.

## Retirement process

1. Model owner proposes retirement (accuracy drift, CVE, superseded champion, end of support).  
2. Remove from serving desired state via Argo; revoke signing trust if compromised.  
3. Archive bundle + evidence; update model card status to retired.  
4. Close related risks or transfer to successor model.

## AI risks

| ID | Risk | L | I | Score | Treatment | Owner | Due | Residual | Acceptance | Expiry |
|---|---|---|---|---|---|---|---|---|---|---|
| AIR-01 | Users over-trust CIFAR accuracy on real photos | 4 | 3 | 12 | Document prohibited uses; uncertain flags later | Model | Rel A | Medium | Accepted Rel E (`risk_acceptance_release_e.md`) | 2026-11-01 |
| AIR-02 | Test leakage invalidates metrics | 2 | 4 | 8 | Locked test; contract tests | Data | Rel A | Low | — | — |
| AIR-03 | Overfitting / weak generalization | 3 | 3 | 9 | Val protocol; Phase 7 aug/BN/dropout + ablations; model card; residual until Phase 8–9 rigor/champion | Model | Rel B | Medium | Treating (Phase 7 evidence) | — |
| AIR-04 | Irreproducible champion | 2 | 4 | 8 | Seeds, configs, identities | Model | Rel B | Low | — | — |
| AIR-05 | High-confidence OOD errors in API | 3 | 4 | 12 | Robustness tests; confidence policy; OIDC/RBAC + flags (Phase 11+) | Model/App | Rel B/C | Medium | Accepted Rel E with API controls | 2026-11-01 |

## Cyber risks

| ID | Risk | L | I | Score | Treatment | Owner | Due | Residual | Acceptance | Expiry |
|---|---|---|---|---|---|---|---|---|---|---|
| CYB-01 | Secrets in source or logs | 2 | 5 | 10 | Pre-commit secret scan; redaction; stop-promote | Security | Rel 0/1 | Low | — | — |
| CYB-02 | Anonymous or weak API auth | 3 | 5 | 15 | OIDC mandatory in prod; deny-by-default RBAC | Security/App | Rel C | Low after C | — | — |
| CYB-03 | Image parse DoS / zip bombs | 3 | 4 | 12 | Size/decompress/timeouts | App | Rel C | Medium | — | — |
| CYB-04 | Unsigned image/model admitted | 2 | 5 | 10 | Sign + admission policies | Platform/Sec | Rel C/D | Low | — | — |
| CYB-05 | Over-broad IAM / public exposure | 2 | 5 | 10 | Policy-as-code; negative tests | Platform/Sec | Rel D | Low | — | — |
| CYB-06 | Long-lived cloud keys in CI | 2 | 5 | 10 | GitHub OIDC only | Security | Rel 0/1 | Low | — | — |
| CYB-07 | Known torch advisories on pinned 2.7.1 / torchvision 0.22.1 | 2 | 3 | 6 | Pin latest compatible pair; track upgrade; offline train risk limited; block prod image on unreviewed critical exploitability | Security | Rel C | Medium | Accepted through Phase 16 desk RC; reassess at ORR / upgrade | 2026-11-01 |

## Risk appetite

- Scores ≥ 15: must be treated before production promotion.  
- Unaccepted high AI risk blocks model promotion even if accuracy passes.  
- Educational offline baseline may proceed with documented medium residuals (AIR-01).
