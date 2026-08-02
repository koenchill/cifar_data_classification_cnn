# Runbook — Scale, Eviction, and Node Loss

## Capacity baseline (Phase 12)

| Resource | Request | Limit |
|---|---|---|
| CPU | 250m (staging) / 500m (prod) | 1 / 1500m |
| Memory | 512Mi / 1Gi | 2Gi |
| HA floor | HPA `minReplicas` ≥ 2 (prod ≥ 3) | |

Do **not** guess limits — re-run `scripts/measure_capacity.py` before changing.

## Scale up (load)

1. Confirm HPA: `kubectl -n cifar-cnn get hpa api -o yaml`
2. Temporary ceiling: patch HPA `maxReplicas` via overlay PR (preferred) or emergency:  
   `kubectl -n cifar-cnn patch hpa api --type merge -p '{"spec":{"maxReplicas":10}}'`
3. Watch: `kubectl -n cifar-cnn get pods -l app.kubernetes.io/name=cifar-cnn-api -w`

## Voluntary eviction / drain

1. Confirm PDB `minAvailable: 1` (staging) / higher floor via replica count (prod).
2. Drain one node in the inference pool:  
   `kubectl drain <node> --ignore-daemonsets --delete-emptydir-data`
3. Expect rolling reschedule across zones (topology spread).
4. Uncordon when healthy.

## Node loss (involuntary)

1. Check available replicas and alerts (`CifarCnnApiReplicaShortage`).
2. If stuck Pending: verify inference pool taints/labels and subnet capacity.
3. Do not remove PDB to force eviction.

## Positive/negative expectations

| Event | Expected |
|---|---|
| Rolling update | maxUnavailable=0; continuous ready endpoints |
| Single zone drain | Pods remain in other zones |
| Scale to max | Respect ResourceQuota; no privileged escalation |
| Default-deny NetworkPolicy | East-west to unrelated namespaces blocked |
