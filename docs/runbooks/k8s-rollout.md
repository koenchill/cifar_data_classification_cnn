# Runbook — API Rolling Update

## Preconditions

- Image digest signed and scanned (Phase 12 `ci-image`)
- Overlay image digest updated (never `:latest` alone)
- Staging soak green before prod

## Procedure

1. Update `deploy/kustomize/overlays/<env>/kustomization.yaml` `images[].digest`.
2. Open PR; CI renders `kubectl kustomize` and policy tests.
3. After merge, Argo CD (Phase 15) syncs desired state — or for lab:  
   `kubectl apply -k deploy/kustomize/overlays/staging`
4. Watch rollout:  
   `kubectl -n cifar-cnn rollout status deploy/api`
5. Confirm PDB/HPA still healthy:  
   `kubectl -n cifar-cnn get pdb,hpa,deploy`

## Rollback

1. Revert overlay digest to previous known-good digest.
2. Sync / apply.
3. If pods CrashLoop on secrets: check ExternalSecret `api-runtime` status and IRSA role.

## Abort criteria

- Available replicas < 2 for >5m
- p95 latency alert firing
- Elevated 5xx > SLO
