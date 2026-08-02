# Runbook — Continuity and Restore

## Objectives

| Item | RPO (target) | RTO (target) |
|---|---|---|
| Desired state (Git) | 0 (Git is SoT) | &lt; 30 m re-sync |
| Model bundle + image digest | Last known-good Git commit | &lt; 1 h promote/revert |
| Terraform state | S3 versioning + DynamoDB lock (bootstrap module) | &lt; 4 h recover state access |
| Secrets | External Secrets / IdP — not in Git | &lt; 1 h rotate + sync |

## Restore paths

1. **App config / image** — revert overlay digest PR; Argo self-heal (`gitops-rollback.md`).  
2. **Cluster namespace wipe** — re-apply Argo app-of-apps; External Secrets rehydrate; do not recreate secrets from chat logs.  
3. **State backend loss** — restore S3 object versions; re-init Terraform with lock table; plan before apply.  
4. **Model rollback** — previous bundle path / prior digest in overlay; verify HMAC/cosign before traffic.

## Continuity tabletop

See `docs/evidence/release-e/alert_restore_tabletop.md`. Live AWS restore drill remains an ops precondition before first customer traffic.
