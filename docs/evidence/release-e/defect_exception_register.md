# Defect and Exception Register — Release Candidate (Phase 16)

| Field | Value |
|---|---|
| Date | 2026-08-02 |
| Policy | `docs/governance/quality_release_policy.md` |
| Rule | No Critical on RC; High must be fixed or formally accepted with control + expiry |

## Open / accepted items

| ID | Sev | Title | Status | Compensating control | Owner | Expiry |
|---|---|---|---|---|---|---|
| CYB-07 | Medium | Torch/torchvision pinned advisories (`pip-audit`) | **Accepted** (carry-forward) | Offline/train threat limited; prod image reassess; track upgrade | Security | 2026-11-01 |
| AIR-01 | Medium | Over-trust of CIFAR accuracy on real photos | **Accepted** (intended-use) | Prohibited-use docs; model card limits; no safety claims | AI owner | Review at ORR |
| AIR-05 | Medium | High-confidence OOD errors | **Treating / residual** | OIDC/RBAC + confidence flags; not anonymous surface | Model/App | ORR |
| DEF-16-01 | Medium | No live EKS/Argo customer-account soak | **Accepted** Rel E desk close | Manifest/policy tests + runbooks + tabletops; **block first prod traffic** until ORR bootstrap checklist | Platform | Until live soak signed |
| DEF-16-02 | Low | Matplotlib/ONNX deprecation warnings in pytest | **Accepted** | Non-flaky; does not fail gates; track upstream | Eng | Next train |

## Closed this verification

| ID | Sev | Title | Resolution |
|---|---|---|---|
| — | — | No new Critical/High defects found in consolidated `pytest -q` | N/A |

## Flaky gates

| Gate | Observation | Disposition |
|---|---|---|
| `ci-pr` lint-test | Stable green on Phase 15 merge; Phase 16 local 110 passed | No unexplained flake |
| `pip-audit` | `continue-on-error` with CYB-07 | Documented exception, not silent ignore |

## Sign-off note

No Critical defects. High items: none open without acceptance. Medium residuals listed above with owners and expiry/review points.
