# API Security Boundary (Phase 11)

## Endpoints

| Method | Path | Auth | Notes |
|---|---|---|---|
| GET | `/health` | Public | Liveness |
| GET | `/ready` | Optional (`CIFAR_CNN_AUTH_READY`) | Model load status only |
| GET | `/v1/metadata` | Scope `metadata:read` | Classes, input constraints, policy |
| POST | `/v1/predict` | Scope `predict:invoke` | Multipart `file` image; no URL fetch |

## Controls

- **OIDC/JWT**: issuer, audience, exp, signature (`static` HS256 for dev/CI; `jwks` RS256 for prod)
- **RBAC**: deny-by-default scopes; roles `predictor` / `viewer` / `admin` map to scopes
- **Input**: content-type, magic bytes, max bytes, 32×32 RGB, decompression pixel bound
- **Abuse**: per-subject rate limit, concurrency semaphore, predict timeout, `top_k` cap → 413/429/504
- **Audit**: structured events with subject, action, model id, status, latency; never tokens/image bytes
- **Config**: production forbids static OIDC and anonymous predict

## Non-claims

Softmax confidence and decision flags are not proof of correctness (see Phase 8 policy).
