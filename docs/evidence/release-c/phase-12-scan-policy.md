# Phase 12 Image Scan Policy

| Severity | Gate |
|---|---|
| CRITICAL (fixed available) | Block image publish (`ci-image` Trivy `exit-code: 1`) |
| CRITICAL (unfixed) | `ignore-unfixed: true`; track in risk register |
| HIGH (torch stack) | Accepted under **CYB-07** until 2026-11-01 with rebuild SLA |
| Medium/Low | Follow `supply_chain_policy.md` cadence |

Ignore file: `deploy/docker/trivyignore` (keep empty unless a named CRITICAL exception is required).

Signature verify (publish jobs):

```text
cosign verify ghcr.io/<org>/<repo>/api@sha256:<digest> \
  --certificate-identity-regexp '...' \
  --certificate-oidc-issuer https://token.actions.githubusercontent.com
```
