# Application Security Scanning (SAST / DAST / SCA)

| Field | Value |
|---|---|
| Workflow | `.github/workflows/ci-security.yml` |
| Permissions | `contents: read`, `id-token: none` (no deploy) |
| Artifacts | `sast-reports`, `sca-reports`, `dast-reports` |

## SAST (static)

| Tool | Scope | Gate |
|---|---|---|
| Bandit | `src/` | Fail on findings (`pyproject.toml` bandit config) |
| Semgrep | `src/` with `p/python` + `p/owasp-top-ten` | Fail on error-severity matches (`--error`) |

Also retained in `ci-pr` lint-test: Bandit + `detect-secrets`.

## SCA (software composition)

| Tool | Scope | Gate |
|---|---|---|
| pip-audit | Installed `[dev]` env | New IDs must be allowlisted via `scripts/check_sca_allowlist.py` |
| Trivy fs | Repository filesystem | Fail on **CRITICAL** unfixed |
| OSV-Scanner | Source tree | Report artifact (inventory) |

Allowlist: `security/sca-allowlist.txt` (expiry **2026-11-01**). Add IDs only with risk acceptance / compensating controls (see `risk_register.md`, `vulnerability-lifecycle.md`).

Container image SCA/signing remains in `ci-image` (Trivy image CRITICAL + cosign).

## DAST (dynamic)

| Tool | Target | Gate |
|---|---|---|
| OWASP ZAP baseline | Ephemeral API from `scripts/start_dast_target.py` | Fail on ZAP **FAIL** severities (`-I` ignores WARN noise) |

Target runs in development mode with a packed FakeCIFAR-sized SimpleCNN bundle, static HS256 OIDC, anonymous predict **disabled**.

## Required checks (GitHub branch protection)

Enabled on **`dev`** and **`main`** (strict / up-to-date required):

`lint-test`, `iam-negative-guard`, `title`, `sast`, `sca`, `dast`
