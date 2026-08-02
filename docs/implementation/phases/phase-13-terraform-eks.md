# Phase 13 — Terraform Cloud Foundation: Network, IAM, Encryption, and EKS

| Field | Value |
|---|---|
| Release | D |
| Depends | Phases 1 and 12 |
| Status | `todo` |
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

  - [ ] Encrypted versioned locked access-logged remote state; per-env; scoped plan/apply + approvals

### Network + cluster

  - [ ] Multi-AZ VPC; private nodes; Flow Logs; managed EKS; IRSA/Pod Identity; secret encryption

### IAM + registry + policy-as-code

  - [ ] Role catalog with boundaries; encrypted immutable ECR; plan policy tests

## Deliverables

- `Terraform bootstrap + env stacks/modules; plan artifacts; architecture/cost assumptions`
- `docs/evidence/release-d/phase-13-gate.md`

## Exit gate

- [ ] fmt/validate/test/plan + policy checks pass
- [ ] State restore + least-privilege negative tests pass; staging reproducible

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

- [ ] All workstream tasks complete
- [ ] Deliverables exist at listed paths
- [ ] Exit gate criteria satisfied
- [ ] Verify commands recorded/pass
- [ ] No global stop condition triggered
