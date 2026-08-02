# System Context and Boundary

## System boundary

**In scope**

- CIFAR-10 data loading, guide-exact `SimpleCNN`, training, evaluation, visualization, model persistence
- Later: improved models, transfer learning, ONNX/governed bundle
- FastAPI inference service with OIDC/RBAC/rate limits/audit
- Hardened Docker image; optional AWS VPC/EKS/ECR via Terraform; Argo CD GitOps
- Governance docs, evidence packs, CI trust foundation

**Out of scope (initial)**

- Multi-tenant SaaS billing
- Training on customer private datasets
- Real-time video / detection / segmentation products
- Guaranteeing accuracy on non-CIFAR real-world photos

## Context diagram (logical)

```text
[Developer workstation]
    | train/eval (offline)
    v
[src/cifar_cnn + configs] ---> [artifacts/models] ---> [model bundle]
                                      |
                                      v
[Authenticated client] --OIDC--> [API / FastAPI] --load--> [model]
                                      |
                     +----------------+----------------+
                     v                                 v
              [Audit / metrics]                 [OIDC IdP]
                     |
                     v
        [Docker] -> [EKS via Argo CD] -> [AWS: VPC, IAM, ECR, logs]
```

## Dependencies

| Layer | Dependency |
|---|---|
| Data | CIFAR-10 via Torchvision; local `./data` cache |
| Model software | Python, PyTorch, Torchvision, Matplotlib |
| Serving | FastAPI stack (Phase 11+); OIDC issuer |
| Supply chain | GitHub Actions (OIDC), base images by digest, SBOM/signing |
| Cloud (enterprise path) | AWS (VPC, EKS, ECR, KMS, IAM), Terraform state backend, Argo CD |
| Fallback path | Single-host hardened Docker (not equivalent to EKS reference) |

## Trust boundaries

1. Developer laptop ↔ git remote  
2. CI identity ↔ cloud roles (short-lived OIDC only)  
3. Internet client ↔ ingress/API (authn/authz required in prod)  
4. API ↔ model weights / secrets (runtime retrieval; no secrets in git)  
5. Git desired state ↔ Argo CD ↔ cluster (pull-based; no CI cluster-admin apply)

## Data classes

| Class | Examples | Handling |
|---|---|---|
| Public benchmark | CIFAR-10 | Cite license; lineage in data card |
| Model artifacts | `.pth`, ONNX, bundles | Hash/sign before release |
| Secrets | OIDC client secrets, cloud creds | Runtime only; never commit |
| Telemetry | Audit logs, metrics | No image bytes / tokens in logs |
