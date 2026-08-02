# Supply Chain Policy

## Pinning

| Artifact | Rule |
|---|---|
| GitHub Actions | Pin by **commit SHA** (comment with version tag) |
| Container base images | Pin by **digest** (`repo@sha256:…`) |
| Python deps | Pin in `pyproject.toml` + lockfile (`requirements.lock`) |
| Pre-commit hooks | Pin by immutable `rev` |

## SBOM

- **Chosen format:** CycloneDX JSON (primary); SPDX acceptable as alternate export.  
- Generated at image build (Phase 12) and retained with release evidence.

## Update cadence

| Class | Cadence |
|---|---|
| Runtime deps (torch stack) | Monthly review; sooner on critical CVE |
| Dev tools (ruff, mypy, pytest) | Monthly |
| Actions / base images | Biweekly scan; patch critical within SLA |
| Pre-commit hooks | Monthly |

## Vulnerability severity / exception SLAs

| Severity | Remediate or exception |
|---|---|
| Critical (exploitable) | 7 days or block release |
| High | 30 days or formal exception ≤ 30 days |
| Medium | 90 days |
| Low | Next scheduled refresh |

Exceptions follow `risk_register.md` (owner, compensating control, expiry).

## Rebuild

Rebuild and resign images even when application code is unchanged if base image or dependency CVEs require it.
