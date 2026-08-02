# Service Level Objectives (Approved — Phase 17)

| Field | Value |
|---|---|
| Status | **Approved** for Release E ORR |
| Approver | Final release approver (`koenchill`) |
| Date | 2026-08-02 |
| Measurement window | Calendar month (prod); staging informational |

## Approved SLOs

| SLI | SLO | Alert / paging |
|---|---|---|
| Availability (successful non-5xx on served traffic; `/ready` green) | ≥ **99.5%** monthly | Critical: available replicas &lt; 2 for 5m (`CifarCnnApiReplicaShortage`) |
| Predict latency p95 (warm pod, allowed image size, authenticated) | ≤ **500 ms** | Warning: p95 &gt; 500 ms for 15m (`CifarCnnApiHighLatency`) |
| Error rate (5xx / all) | ≤ **1%** under target load | Warning: ratio &gt; 1% for 10m (`CifarCnnApiHighErrorRate`) |
| Auth denials (401/403 rate) | No sustained unexplained spike | Security: rate &gt; 5/s for 10m (`CifarCnnApiAuthDeniesSpike`) |

## Notes

- ConfigMap `api-observability` mirrors these targets for operators.
- Phase 12 capacity envelope (CPU/mem) remains the sizing baseline for meeting latency SLO.
- Staging may run below availability SLO during experiments; prod overlays must not.
