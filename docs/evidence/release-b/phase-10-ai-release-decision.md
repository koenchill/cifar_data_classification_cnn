# Release B — AI RMF Release Decision

| Field | Value |
|---|---|
| Date | 2026-08-01 |
| Decision | **Promote Release B bundle candidate** (educational / non-production) |
| Champion | `simple_cnn_baseline` (Phase 09 rule) |
| Bundle | `models/bundles/simple_cnn-1.0.1` (HMAC-signed manifest) |

## Govern / Map / Measure review

| Function | Status | Evidence |
|---|---|---|
| Govern | OK | RACI, intended use, quality policy, AI RMF profile |
| Map | OK | Data/model cards; prohibited real-world claims |
| Measure | OK | Phases 5–8 metrics, robustness, Grad-CAM, calibration |
| Manage | Conditional | Monitors/thresholds deferred to API/ops (Phases 11–17); rollback via `CURRENT` pointer |

## AI risk gate

| ID | Residual | Promotion impact |
|---|---|---|
| AIR-01 | Medium | Accepted for offline/demo with model-card prohibitions |
| AIR-02 | Low | Treated (locked test; selection forbids test fields) |
| AIR-03 | Medium | Treating; not a high unresolved blocker for B offline bundle |
| AIR-04 | Low | Treated (seeds, configs, identities, signed bundle) |
| AIR-05 | Medium | Compensating control: confidence policy (Phase 08); **prod API blocked until Phase 11** |

**Rule applied:** High unresolved AI risks block promotion. No high-severity AI risk is unowned; AIR-05 remains medium with explicit prod-block until secure API lands.

## Rollback / retirement

- Rollback: `rollback_bundle(models/bundles, previous_version)` after verify  
- Retirement: supersede bundle version; revoke HMAC key if compromised; update model card status  

## Non-claims

Not NIST certified. Not production-serving without Release C controls.
