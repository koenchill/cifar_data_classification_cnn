# Cursor Execution Plan

Operational index for the six-release / eighteen-phase enterprise plan. Agents execute **exactly one phase per session** unless the user explicitly expands scope.

## Student-guide compliance (non-negotiable for Release A)

Release A (Phases **1 toolchain + 2–5**) must satisfy the course guide with **zero gaps**.

| Doc | Role |
|---|---|
| [`GUIDE_TRACEABILITY.md`](GUIDE_TRACEABILITY.md) | Requirement-by-requirement matrix (Steps 1–7, §§1/2/4, questions) |
| [`../evidence/release-a/student_guide.md`](../evidence/release-a/student_guide.md) | Canonical guide text |
| [`../evidence/release-a/guide_tough_questions_source.md`](../evidence/release-a/guide_tough_questions_source.md) | All 20 tough questions (source complete) |

**Rules**

1. Baseline path implements guide APIs/hyperparams exactly (`ToTensor`+`Normalize(0.5…)`, loaders, `SimpleCNN` layers, CE+Adam`0.001`, 10 epochs, 10k accuracy, 8-image Actual/Predicted viz, `cnn_model.pth`).
2. Guide training-loop bug (missing `running_loss += loss.item()`) is **fixed and documented**, not copied.
3. Enterprise features are **additive** and must not alter baseline guide behavior (val split, device, confidence overlays, later BN/aug/API/K8s).
4. Release A exit requires every matrix row in `GUIDE_TRACEABILITY.md` marked done with evidence links.

## Delivery map

| Release | Phases | Outcome | Evidence dir |
|---|---|---|---|
| 0 — Governance & secure foundation | 0–1 | Boundary, owners, AI RMF profile, threat model, Zero Trust target, secure repo/CI trust | `docs/evidence/release-0/` |
| A — Guide-compliant ML baseline | 2–5 | Exact CIFAR-10/SimpleCNN workflow, leakage-safe eval, saved model, visuals, guide Qs | `docs/evidence/release-a/` |
| B — Production ML & AI assurance | 6–10 | Repro training, improved models, rigor/robustness, transfer, champion, governed bundle | `docs/evidence/release-b/` |
| C — Secure app & container | 11–12 | OAuth/OIDC FastAPI, rate/RBAC/audit, hardened signed image, compute envelope | `docs/evidence/release-c/` |
| D — Kubernetes & GitOps | 13–15 | Terraform AWS/EKS, hardened K8s runtime, Argo CD promotion | `docs/evidence/release-d/` |
| E — Continuous assurance & ops | 16–17 | Full test evidence, SLO/chaos/DR, IR/vuln ops, AI-risk acceptance, prod release | `docs/evidence/release-e/` |

## Phase index

| Phase | Title | Depends | Card |
|---|---|---|---|
| 0 | Governance, intended use, risk framing | — | [phase-00](phases/phase-00-governance.md) |
| 1 | Secure repo, developer env, CI trust | 0 | [phase-01](phases/phase-01-secure-repo-ci.md) |
| 2 | CIFAR-10 data contract & leakage-safe splits | 1 | [phase-02](phases/phase-02-data-contract.md) |
| 3 | Guide-exact SimpleCNN & model integrity | 2 | [phase-03](phases/phase-03-simplecnn.md) |
| 4 | Correct guide baseline training | 3 | [phase-04](phases/phase-04-baseline-training.md) |
| 5 | Baseline eval, viz, persistence, learning evidence | 4 | [phase-05](phases/phase-05-baseline-evaluation.md) |
| 6 | Production training controls & experiment tracking | 5 | [phase-06](phases/phase-06-training-controls.md) |
| 7 | Improved CNN, augmentation, BN, dropout | 6 | [phase-07](phases/phase-07-improved-cnn.md) |
| 8 | Rigorous evaluation, robustness, Grad-CAM | 6–7 | [phase-08](phases/phase-08-rigorous-evaluation.md) |
| 9 | Transfer learning & champion selection | 8 | [phase-09](phases/phase-09-transfer-champion.md) |
| 10 | Governed model bundle, ONNX, AI release gate | 9 | [phase-10](phases/phase-10-model-bundle.md) |
| 11 | Secure FastAPI: OIDC, RBAC, limits, audit | 10 | [phase-11](phases/phase-11-secure-api.md) |
| 12 | DevSecOps Docker artifact & compute envelope | 11 | [phase-12](phases/phase-12-docker-envelope.md) |
| 13 | Terraform cloud foundation (network/IAM/EKS) | 1, 12 | [phase-13](phases/phase-13-terraform-eks.md) |
| 14 | Hardened K8s runtime, network, capacity, observability | 13 | [phase-14](phases/phase-14-k8s-runtime.md) |
| 15 | Argo CD GitOps, promotion, drift control | 14 | [phase-15](phases/phase-15-argocd-gitops.md) |
| 16 | Comprehensive verification & QA | 2–15 | [phase-16](phases/phase-16-verification-qa.md) |
| 17 | Operational readiness, AI RMF Manage, release | 16 | [phase-17](phases/phase-17-ops-release.md) |

## Agent operating rules

1. **One phase.** Read the phase card; implement only its workstreams.
2. **Path discipline.** Edit only `Allowed paths`. Do not invent parallel trees.
3. **Exit gate first.** A phase is done only when exit-gate checks pass and evidence paths exist.
4. **No silent scope creep.** Guide baseline (Phases 1 toolchain + 2–5) stays exact per `GUIDE_TRACEABILITY.md`; improvements begin at Phase 7.
5. **Security is continuous.** Secrets never enter git; OIDC/RBAC/rate/audit failures block Release C+.
6. **Claims hygiene.** No “NIST certified”; no unsupported real-world safety/performance claims.
7. **Deployment honesty.** Local Docker ≠ EKS reference architecture.

## Global stop conditions

| Condition | Response |
|---|---|
| Test-set leakage / untraceable lineage / irreproducible champion | Invalidate; rerun from last trusted phase |
| Secret in source, image, plan/state, or logs | Stop promotion; revoke/rotate; purge; add regression; rebuild |
| Critical exploitable finding | Block until remediated or formally accepted (owner + expiry) |
| Unsigned/unverifiable image or model bundle | Deny revoke/admission; rebuild via trusted pipeline |
| Excessive IAM/RBAC/network or public exposure | Block apply until least-privilege + negative tests pass |
| Capacity/HPA/rollout/node-loss/soak breaches SLO | Resize; retest; update assumptions before release |
| OIDC/RBAC/rate-limit/audit failure | Block app release (mandatory, not backlog) |
| Unaccepted high AI risk / missing monitor-rollback owner | Block model promotion even if accuracy passes |

## Suggested session prompt template

```text
Execute Phase <N> only per docs/implementation/phases/phase-<NN>-*.md.
Respect Allowed paths / Forbidden paths.
Mark task checkboxes as you complete them.
Stop at Exit gate; summarize evidence written and remaining blockers.
Do not start Phase <N+1>.
```

## Decision boundary

| Approach | Use |
|---|---|
| Hardened Docker on one small host | Dev/demo/portfolio fallback; early integration |
| Managed EKS + Terraform + Argo CD | Full enterprise path for Releases D–E |
