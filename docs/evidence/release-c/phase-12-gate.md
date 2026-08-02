# Phase 12 Gate — Docker Artifact & Compute Envelope (Release C)

| Field | Value |
|---|---|
| Phase | 12 — DevSecOps Docker envelope |
| Release | C |
| Date | 2026-08-01 |
| Status | Pass (local verify + CI image workflow) |

## Exit criteria

- [x] Multi-stage digest-pinned image; non-root `10001`; compose `read_only` / `cap_drop` / `no-new-privileges`
- [x] Supply-chain workflow: Hadolint, Trivy CRITICAL, SBOM (publish), provenance, cosign keyless sign
- [x] Deploy-by-digest rule documented; mutable-tag-only promotion forbidden
- [x] Capacity recommendation recorded (`phase-12-capacity.json`)
- [x] Critical findings remediated or accepted (CYB-07 torch residual; CRITICAL gate with ignorefile)

## Deliverables

| Artifact | Path |
|---|---|
| Dockerfile | `deploy/docker/Dockerfile` |
| Ignorefile | `deploy/docker/dockerignore` |
| Compose envelope | `deploy/docker/compose.yaml` |
| Trivy ignore | `deploy/docker/trivyignore` |
| Image CI | `.github/workflows/ci-image.yml` |
| Build helper | `scripts/docker_build.py` |
| Capacity script | `scripts/measure_capacity.py` |
| Hardening verify | `scripts/verify_image_envelope.py` |
| Architecture | `docs/architecture/docker_envelope.md` |
| Capacity evidence | `docs/evidence/release-c/phase-12-capacity.json` |
| Release decision | `docs/evidence/release-c/release-c-decision.md` |

## Verify

```text
python scripts/verify_image_envelope.py
pytest -q tests/unit/test_docker_envelope.py
python scripts/docker_build.py --tag cifar-cnn-api:local --load
docker build -f deploy/docker/Dockerfile .
```

Local hardening/static verify: **pass**.

| Check | Result |
|---|---|
| `python scripts/verify_image_envelope.py` | Pass |
| `pytest -q tests/unit/test_docker_envelope.py` | Pass (3) |
| `python scripts/docker_build.py --tag cifar-cnn-api:local --load` | Pass |
| Hardened run (`read_only`, `cap_drop ALL`, uid 10001) `/health`+`/ready` | Pass (`ready=true`) |
| Local image digest | `sha256:6f43777bf8ad41ffaf3bf16645438463ebe36653b6453252e6bb7166101004c1` |

GHCR publish + cosign keyless + CycloneDX SBOM: `ci-image` workflow on push to `dev`/`main`.

## Release C closure

With Phases **11** (secure API) and **12** (hardened image + capacity), **Release C is complete** for the application boundary + Docker demo path. EKS/Terraform/Argo remain Releases D–E and are **not** claimed by this Docker envelope.
