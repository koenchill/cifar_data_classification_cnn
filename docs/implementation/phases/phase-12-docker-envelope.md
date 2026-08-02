# Phase 12 — DevSecOps Docker Artifact and Compute Envelope

| Field | Value |
|---|---|
| Release | C |
| Depends | Phase 11 |
| Status | `todo` |
| Evidence | `docs/evidence/release-c/phase-12-gate.md` |

## Objective

Build one hardened signed image and derive compute requirements from measurement.

## Allowed paths

- `deploy/docker/`
- `.github/workflows/`
- `docs/architecture/`
- `docs/evidence/release-c/`
- `scripts/`
- `tests/`

## Forbidden

- Compilers/caches/shell/credentials/dataset/training code in final image unless required
- Deploy by mutable tag without digest

## Workstreams

### Image hardening

  - [ ] Multi-stage; pin base by digest; non-root; read-only root; drop caps; no-new-privileges

### Supply chain

  - [ ] Lint; scan; SBOM; provenance; sign; deploy by digest; rebuild/vuln SLA

### Runtime + capacity

  - [ ] Preload model; benchmark workers; measure latency/throughput/CPU/memory/startup/pull/errors

## Deliverables

- `deploy/docker/Dockerfile; signed digest; SBOM/provenance; scan report; capacity recommendation`
- `docs/evidence/release-c/phase-12-gate.md`

## Exit gate

- [ ] Critical findings remediated or accepted; non-root/read-only verified
- [ ] Signature/SBOM/provenance verify; approved requests/limits; Release C complete

## Verify

```text
docker build -f deploy/docker/Dockerfile .
```

## Cursor prompt (copy)

```text
Execute Phase 12 only per docs/implementation/phases/phase-12-docker-envelope.md.
Respect Allowed paths and Forbidden paths.
Complete workstreams in order; check off tasks as done.
Write exit-gate evidence to docs/evidence/release-c/phase-12-gate.md.
Do not start the next phase.
```

## Done when

- [ ] All workstream tasks complete
- [ ] Deliverables exist at listed paths
- [ ] Exit gate criteria satisfied
- [ ] Verify commands recorded/pass
- [ ] No global stop condition triggered
