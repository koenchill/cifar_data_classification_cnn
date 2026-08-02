# Requirements-to-Test Matrix (Release E / Phase 16)

Maps committed release requirements to automated suites and desk-review evidence. Guide rows remain authoritative in `docs/implementation/GUIDE_TRACEABILITY.md`.

| Req ID | Requirement | Primary tests / evidence | Gate |
|---|---|---|---|
| A-GUIDE | Student guide contract (transforms, SimpleCNN, train/eval/save) | `tests/unit/test_data_contract.py`, `test_simple_cnn.py`, `test_trainer.py`, `tests/integration/test_baseline_eval.py`; GUIDE_TRACEABILITY | A |
| B-CTRL | Training controls / no test leakage | `tests/unit/test_training_controls.py`, `test_aug_train_only.py`, `test_splits.py` | B |
| B-EVAL | Rigorous eval + champion selection | `tests/unit/test_metrics_fixtures.py`, `tests/integration/test_champion_selection.py` | B |
| B-BUNDLE | Signed/hashed model bundle + ONNX parity | `tests/unit/test_bundle_tamper.py`, `test_onnx_parity.py` | B |
| C-API | OIDC/JWT, RBAC, rate limits, audit, image limits | `tests/security/*`, `tests/contract/test_api_contract.py`, `tests/e2e/test_predict_smoke.py` | C |
| C-IMG | Hardened image envelope + capacity | `tests/unit/test_docker_envelope.py`; `docs/evidence/release-c/phase-12-*` | C |
| D-TF | Terraform policy + no static AWS keys in CI | `tests/terraform/*`; `.github/workflows/terraform.yml` | D |
| D-K8S | Restricted PSS, NetPol, HA/capacity | `tests/integration/test_k8s_policy.py` | D |
| D-GITOPS | Argo isolation, digest promotion, admission | `tests/integration/test_argocd_gitops.py`; `gitops-promote.yml` | D |
| E-QA | Consolidated verification + reviews | This matrix; `verification_results.json`; review/sign-off pack | E |
| SEC-01 | No secrets in source | `detect-secrets` (ci-pr); CYB-01 | 0/E |
| SEC-02 | Fail-closed security config | `tests/security/test_config_fail_closed.py` | C/E |
| SEC-03 | Deny anonymous prod predict | `tests/security/test_oidc_rbac.py` | C/E |
| SLO-01 | Candidate availability/latency/error thresholds | Policy + PrometheusRule; Phase 17 ORR finalizes | E→17 |
| AI-01 | Intended use / overclaim controls | `docs/governance/intended_use.md`; model cards; AIR-01 | A/E |

## Suite inventory (pytest collection)

| Layer | Path | Role |
|---|---|---|
| Unit | `tests/unit/` | Data/model/train/bundle/docker contracts |
| Security | `tests/security/` | Authz, limits, audit redaction, fail-closed |
| Contract | `tests/contract/` | API schema/behavior |
| Integration | `tests/integration/` | Eval, champion, K8s, GitOps |
| E2E | `tests/e2e/` | Predict smoke |
| Infra | `tests/terraform/` | Policy-as-code + IAM negative |
| Release meta | `tests/release/` | Phase 16 evidence presence |

## Explicit non-coverage (accepted for RC desk scope)

| Gap | Treatment |
|---|---|
| Live EKS soak / pen test against customer account | Tabletop + deferred to live bootstrap; tracked in defect register |
| Full CIFAR-10 training in CI | Forbidden; FakeCIFAR/smoke only |
| Prod IdP end-to-end SSO | Placeholder OIDC config; ORR Phase 17 |
