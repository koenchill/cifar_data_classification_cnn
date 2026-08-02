# Intended Use Statement

| Field | Value |
|---|---|
| System | CIFAR-10 CNN image classification service |
| Owner | koenchill (AI system owner) |
| Status | Draft for Phase 0 approval |
| Mapped framework | Selected NIST AI RMF outcomes (not a certification claim) |

## Intended uses

1. **Educational / portfolio demonstration** of a guide-compliant CIFAR-10 `SimpleCNN` baseline (Release A).
2. **Controlled research and engineering** of improved models, evaluation, and transfer learning on CIFAR-10 (Release B).
3. **Authenticated inference API** that classifies user-supplied images into the **ten CIFAR-10 class labels** under rate limits and audit controls (Release C+).
4. **Reference enterprise delivery** of that API on hardened Docker and optionally AWS EKS via Terraform/Argo CD (Releases C–E).

## Intended users

| User | Role |
|---|---|
| Student / developer (primary) | Trains, evaluates, and documents the baseline and improvements |
| Reviewer / interviewer | Consumes evidence, model cards, and demos |
| Authenticated API client | Calls `/v1/predict` with allowed image payloads |
| Platform / security / SRE owners | Operate, monitor, and approve releases |

## Stakeholders

- AI system / model / data / application owners (see `raci.md`)
- Security and SRE/operations
- Final release approver
- Optional privacy/legal reviewer when personal data or public deployment expands scope

## Prohibited uses

1. Safety-critical decisions (medical diagnosis, autonomous driving actions, weapons targeting, biometric identification for access control).
2. Claims of real-world accuracy or safety beyond CIFAR-10 benchmark evidence.
3. Processing of prohibited content categories defined by policy (e.g., CSAM); inputs are expected to be ordinary RGB images for CIFAR-like object classes.
4. Unauthenticated public prediction in production unless explicitly risk-accepted with compensating controls.
5. Training or fine-tuning on sensitive personal data without a separate data-protection review.
6. Representing outputs as human identity verification or legal evidence.
7. Claiming NIST certification/endorsement, “production-safe for any imagery,” or equivalent.

## Deployment context

| Context | Allowed |
|---|---|
| Local CPU training / eval | Yes (guide baseline) |
| Local hardened Docker demo | Yes (portfolio / early integration) |
| Staging on EKS | Yes, after Releases C–D gates |
| Production on EKS via Argo CD | Yes, only after Release E ORR and signed digest promotion |

## Risk appetite (initial)

- Accept educational and portfolio residual risk for offline baseline training.
- Do **not** accept unresolved high AI or security risks for production promotion.
- Prefer fail-closed authz, unsigned-artifact denial, and explicit residual-risk acceptance with owner + expiry.
