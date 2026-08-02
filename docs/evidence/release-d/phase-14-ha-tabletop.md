# Phase 14 HA / Disruption Tabletop

Executed against rendered manifests + runbook procedures (no live EKS required for gate).

| Scenario | Control | Expected outcome |
|---|---|---|
| Rolling update | `maxUnavailable: 0`, probes | Continuous ready pods; digest-only image |
| Pod eviction | PDB `minAvailable: 1` | At least one Ready pod during voluntary disruption |
| Zone loss | topology spread `DoNotSchedule` | Scheduling refuses stacking all pods in one zone when possible |
| Load increase | HPA min 2 / max 6 (staging) | Scale within ResourceQuota |
| East-west probe | default-deny NetPol | Unrelated namespace traffic denied |
| Privilege attempt | restricted PSS + securityContext | Privileged/hostPath/hostNetwork rejected |

Abort if available replicas < 2 for >5m or SLO alerts fire during rollout.
