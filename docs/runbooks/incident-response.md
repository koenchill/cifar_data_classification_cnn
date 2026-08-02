# Runbook — Incident Response

## Severity

| Sev | Examples | Page? |
|---|---|---|
| Sev-1 | Authz bypass, secret leak, unsigned prod image serving, data exfil | Immediate |
| Sev-2 | Availability &lt; SLO, replica shortage, sustained 5xx | Yes |
| Sev-3 | Latency SLO burn, staging-only outage | Business hours |

## Roles

- **Incident commander:** SRE / operations owner  
- **Security lead:** Security owner (Sev-1 security)  
- **App/model:** Application / model owners as needed  

## Standard flow

1. **Detect** — alert, Argo sync fail, or user report.  
2. **Triage** — classify Sev; start timeline notes.  
3. **Contain** — stop bad promotion (revert digest PR); scale/block if abuse; revoke tokens if credential incident.  
4. **Mitigate** — follow `gitops-rollback.md`, `k8s-rollout.md`, or IdP fixes.  
5. **Recover** — confirm `/health` `/ready`, authenticated predict smoke, Argo Healthy.  
6. **Close** — blameless notes; open defect; update risk register if residual.

## Forbidden

- Hotfix production with `kubectl apply` of unsigned or tag-only images.  
- Disabling Kyverno Enforce or auth to “restore service.”
