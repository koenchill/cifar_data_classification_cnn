# Runbook — Observability & SLO Signals

## Signals

| Signal | Source | SLO / threshold |
|---|---|---|
| Availability | Prometheus `http_requests_total` | ≥ 99.9% |
| Latency p95 | histogram quantile | ≤ 100 ms (Phase 12 target) |
| Auth denials | 401/403 rate | Spike alert (security) |
| Replica floor | kube-state-metrics | ≥ 2 available |

## Dashboards

- ConfigMap `grafana-dashboard-cifar-cnn-api` (label `grafana_dashboard=1`)
- Import via Grafana sidecar / dashboard provider

## Alerts

PrometheusRule `cifar-cnn-api` in namespace `cifar-cnn`:

- `CifarCnnApiHighErrorRate`
- `CifarCnnApiHighLatency`
- `CifarCnnApiReplicaShortage` (critical)
- `CifarCnnApiAuthDeniesSpike`

## Logs / traces

Pods emit structured audit logs (no tokens/image bytes). Cluster agents should scrape stdout and forward OTLP using `api-observability` ConfigMap hints (`OTEL_*`).

## Triage

1. Dashboard red on errors → check recent rollout digest and ExternalSecret sync.
2. Latency only → HPA / node pressure / cold start on scale-out.
3. Auth spike → verify OIDC issuer/JWKS and client credentials; check NetworkPolicy egress to IdP.
