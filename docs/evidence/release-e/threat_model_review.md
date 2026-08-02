# Independent Threat-Model Review (Desk) — Phase 16

| Field | Value |
|---|---|
| Baseline | `docs/architecture/threat_model.md` |
| Reviewer role | Security owner (RACI) |
| Date | 2026-08-02 |
| Method | STRIDE + AI abuse-case re-read vs implemented controls |

## Findings

| Threat / abuse | Control present? | Evidence | Verdict |
|---|---|---|---|
| Spoofing (API) | Yes | OIDC/JWT + RBAC suites | Adequate for RC |
| Tampering (model/image) | Yes | Bundle HMAC; digest pin; Kyverno verify | Adequate; live admission pending cluster |
| Repudiation | Yes | Audit redaction tests | Adequate |
| Info disclosure | Yes | Secret scan; audit redaction; no secrets in git | Adequate |
| DoS (predict) | Yes | Rate/size/decompress tests; HPA bounds in manifests | Adequate for measured envelope |
| EoP (CI → prod) | Yes | iam-negative-guard; gitops-promote no kubectl apply | Adequate |
| AI-01 overclaim | Yes | Intended use + cards | Residual accepted |
| AI-02 leakage | Yes | Split/aug tests | Adequate |
| AI-06 silent swap | Yes | Argo + digest + admission policies | Desk-adequate |

## Residual / revise-at-ORR

- Live IdP SSO and Kyverno Enforce on a real cluster not exercised in this phase.
- Threat model status should move from “Phase 0 baseline” to “Phase 16 reviewed” at ORR docs update (Phase 17 allowed paths include architecture cards).

## Decision

**Accept** threat posture for Release E verification desk gate. No Critical gaps. Live pen-test deferred (see `pen_test_tabletop.md`).
