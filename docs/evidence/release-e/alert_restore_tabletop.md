# Alert and Restore Tabletop — Phase 17 ORR

| Field | Value |
|---|---|
| Date | 2026-08-02 |
| Facilitator | SRE / operations owner |
| Refs | Phase 16 `game_day.md`; PrometheusRule; continuity runbook |

## Critical alert proof

| Alert | Rule present in Git | Response runbook | Tabletop outcome |
|---|---|---|---|
| `CifarCnnApiReplicaShortage` | Yes (`prometheusrule.yaml`) | `alert-response.md` | Page → check HA → escalate incident |
| `CifarCnnApiHighErrorRate` | Yes | `alert-response.md` + rollback | Mitigate via digest revert |
| `CifarCnnApiHighLatency` | Yes (500 ms SLO) | capacity / HPA | Aligns with approved SLO |
| `CifarCnnApiAuthDeniesSpike` | Yes | security triage | No auth disable |

## Restore proof

| Scenario | Procedure | Desk result |
|---|---|---|
| Bad prod digest | Revert promotion PR; Argo self-heal | Pass (procedure) |
| Namespace config drift | Self-heal to Git | Pass |
| Bundle integrity fail | Fail closed `/ready`; restore prior bundle | Pass (API tests + runbook) |

## Gap (accepted)

Live firing of alerts into PagerDuty/Slack requires cluster bootstrap — tracked under DEF-16-01 bootstrap checklist, not an unsigned acceptance.
