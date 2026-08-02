# Phase 13 — Terraform Cloud Foundation: Network, IAM, Encryption, and EKS

| Field | Value |
|---|---|
| Release | D |
| Depends | Phases 1 and 12 |
| Status | `done` |
| Evidence | `docs/evidence/release-d/phase-13-gate.md` |

## Objective

Provision the AWS reference platform declaratively with isolated state and least privilege.

## Allowed paths

- `infra/terraform/`
- `.github/workflows/`
- `docs/architecture/`
- `docs/evidence/release-d/`
- `tests/`

## Forbidden

- Wildcard IAM / public exposure without exception
- Long-lived keys for CI apply
- Shared state across environments

## Workstreams

### State/bootstrap

  - [x] Encrypted versioned locked access-logged remote state; per-env; scoped plan/apply + approvals

### Network + cluster

  - [x] Multi-AZ VPC; private nodes; Flow Logs; managed EKS; IRSA/Pod Identity; secret encryption

### IAM + registry + policy-as-code

  - [x] Role catalog with boundaries; encrypted immutable ECR; plan policy tests

## Deliverables

- `Terraform bootstrap + env stacks/modules; plan artifacts; architecture/cost assumptions`
- `docs/evidence/release-d/phase-13-gate.md`

## Exit gate

- [x] fmt/validate/test/plan + policy checks pass
- [x] State restore + least-privilege negative tests pass; staging reproducible

## Verify

```text
terraform -chdir=infra/terraform/envs/staging fmt -check
terraform -chdir=infra/terraform/envs/staging validate
```

## Cursor prompt (copy)

```text
Execute Phase 13 only per docs/implementation/phases/phase-13-terraform-eks.md.
Respect Allowed paths and Forbidden paths.
Complete workstreams in order; check off tasks as done.
Write exit-gate evidence to docs/evidence/release-d/phase-13-gate.md.
Do not start the next phase.
```

## Done when

- [x] All workstream tasks complete
- [x] Deliverables exist at listed paths
- [x] Exit gate criteria satisfied
- [x] Verify commands recorded/pass
- [x] No global stop condition triggered
