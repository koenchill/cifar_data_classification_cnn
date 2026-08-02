# Phase 00 — Governance, Intended Use, and Risk Framing

| Field | Value |
|---|---|
| Release | 0 |
| Depends | None |
| Status | `done` |
| Evidence | `docs/evidence/release-0/phase-00-gate.md` |

## Objective

Establish decision rights, intended use, risk boundaries, and control traceability before implementation.

## Allowed paths

- `docs/governance/`
- `docs/architecture/`
- `docs/evidence/release-0/`
- `docs/implementation/`
- `README.md`

## Forbidden

- src/ tests/ deploy/ infra/ configs/ models/ application code
- Changing application or ML code before Phase 2

## Workstreams

### NIST AI RMF Govern and Map

  - [x] Define intended and prohibited uses, users, stakeholders
  - [x] Define system boundary and data/model/software/cloud dependencies
  - [x] Document potential harms, quality/security risks, deployment context

### Accountability

  - [x] Assign AI system, model, data, application, platform, security, SRE owners
  - [x] Assign privacy/legal reviewer (if applicable) and final release approver
  - [x] Publish RACI

### Risk process

  - [x] Create AI and cyber risk registers with full fields
  - [x] Define exception and retirement processes

### Zero Trust target

  - [x] Map identity, workload/device, network, application, data, visibility, automation, governance
  - [x] Define minimum production maturity

### Security attachment

  - [x] Commit controls: no secrets in source; secure env; auth; OIDC; rate limits; RBAC; audit

### Quality

  - [x] Define release thresholds, SLO candidates, severity taxonomy, defect policy
  - [x] Define evidence retention and change/approval model

## Deliverables

- `docs/governance/ai_rmf_profile.md`
- `docs/governance/raci.md`
- `docs/governance/intended_use.md`
- `docs/architecture/system_context.md`
- `docs/architecture/threat_model.md`
- `docs/governance/risk_register.md`
- `docs/governance/zero_trust_mapping.md`
- `docs/governance/quality_release_policy.md`
- `docs/evidence/release-0/phase-00-gate.md`

## Exit gate

- [x] Owners approve boundary, intended/prohibited uses, risk appetite, control scope, release-gate authority
- [x] Docs state mapped to selected NIST AI RMF outcomes (no NIST certified claim)

## Verify

```text
Test-Path docs/governance/ai_rmf_profile.md
Test-Path docs/governance/raci.md
rg -n "NIST certified" docs/governance  # expect no matches
```

## Cursor prompt (copy)

```text
Execute Phase 00 only per docs/implementation/phases/phase-00-governance.md.
Respect Allowed paths and Forbidden paths.
Complete workstreams in order; check off tasks as done.
Write exit-gate evidence to docs/evidence/release-0/phase-00-gate.md.
Do not start the next phase.
```

## Done when

- [x] All workstream tasks complete
- [x] Deliverables exist at listed paths
- [x] Exit gate criteria satisfied
- [x] Verify commands recorded/pass
- [x] No global stop condition triggered
