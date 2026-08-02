# Docker Compute Envelope (Phase 12 / Release C)

## Honesty boundary

Local hardened Docker is a **portfolio / early-integration** path. It is **not** equivalent to the AWS EKS + Argo CD reference architecture (Phases 13–15).

## Image

| Item | Value |
|---|---|
| Dockerfile | `deploy/docker/Dockerfile` |
| Base | `python@sha256:b18992999dbe963a45a8a4da40ac2b1975be1a776d939d098c647482bcad5cba` (`3.11-slim-bookworm`) |
| User | `10001:10001` (non-root) |
| Model preload | `/app/models/bundles/simple_cnn-1.0.1` |
| Entrypoint | `uvicorn cifar_cnn.api.app:app_factory --factory` |

### Hardening

- Multi-stage build (builder venv → runtime copy)
- Digest-pinned base
- No dataset / training scripts / compilers in runtime stage
- Compose envelope: `read_only`, `cap_drop: [ALL]`, `no-new-privileges`, tmpfs `/tmp`

### Build

```text
python scripts/docker_build.py --tag cifar-cnn-api:local --load
# or
docker buildx build --ignorefile deploy/docker/dockerignore \
  -f deploy/docker/Dockerfile -t cifar-cnn-api:local --load .
```

### Run (lab)

```text
docker compose -f deploy/docker/compose.yaml up --build
```

Production/EKS must inject `APP_ENV=production`, `CIFAR_CNN_OIDC_MODE=jwks`, and JWKS settings. Anonymous predict remains forbidden.

## Supply chain

| Control | Mechanism |
|---|---|
| Lint | Hadolint in `ci-image.yml` |
| Vuln scan | Trivy CRITICAL gate |
| SBOM | CycloneDX via anchore/sbom-action on publish |
| Provenance | BuildKit provenance attestations on push |
| Sign | Cosign keyless (`cosign sign image@digest`) |
| Deploy rule | **Digest only** — mutable tags must not be the sole promotion pin |

Rebuild/resign when base or dependency CVEs require it (see `supply_chain_policy.md` SLAs). Torch residual risk: **CYB-07**.

## Capacity

See `docs/evidence/release-c/phase-12-capacity.json` for measured latency and approved requests/limits for a single replica.
