# Phase 12 — DevSecOps Docker Artifact and Compute Envelope

| Field | Value |
|---|---|
| Release | C |
| Depends | Phase 11 |
| Status | `done` |
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

  - [x] Multi-stage; pin base by digest; non-root; read-only root; drop caps; no-new-privileges

### Supply chain

  - [x] Lint; scan; SBOM; provenance; sign; deploy by digest; rebuild/vuln SLA

### Runtime + capacity

  - [x] Preload model; benchmark workers; measure latency/throughput/CPU/memory/startup/pull/errors

## Deliverables

- `deploy/docker/Dockerfile; signed digest; SBOM/provenance; scan report; capacity recommendation`
- `docs/evidence/release-c/phase-12-gate.md`

## Exit gate

- [x] Critical findings remediated or accepted; non-root/read-only verified
- [x] Signature/SBOM/provenance verify; approved requests/limits; Release C complete

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

- [x] All workstream tasks complete
- [x] Deliverables exist at listed paths
- [x] Exit gate criteria satisfied
- [x] Verify commands recorded/pass
- [x] No global stop condition triggered
