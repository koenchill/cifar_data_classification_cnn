# NIST AI RMF Profile (Selected Outcomes)

| Field | Value |
|---|---|
| System | CIFAR-10 CNN classification |
| Profile type | Selected-outcome mapping |
| Claim language | This project is **mapped to selected NIST AI RMF outcomes**. It does **not** claim NIST certification or endorsement. |

## Govern

| Outcome | Project control |
|---|---|
| Policies, roles, accountability | `intended_use.md`, `raci.md`, `quality_release_policy.md` |
| Risk management process | `risk_register.md` (AI + cyber), exception/retirement |
| Team culture / documentation | Phase evidence under `docs/evidence/`; guide Q&A in Release A |
| AI risk oversight | Model owner + AI-risk review before champion/bundle promotion |

## Map

| Outcome | Project control |
|---|---|
| Context / intended use | `intended_use.md` |
| Categorization | Low physical harm in demo context; higher abuse/security risk if exposed as public API |
| Dependencies | CIFAR-10 + Torchvision; PyTorch; optional pretrained ResNet; OIDC IdP; AWS/EKS; Argo CD |
| Risks / harms | Misclassification overclaim; model theft; abuse of API; supply-chain compromise — see risk register |
| Impacts | Incorrect labels if used outside CIFAR domain; service abuse; credential/data exposure |

## Measure

| Outcome | Project control |
|---|---|
| Baseline metrics | Accuracy on official 10k test (guide); later macro-F1, confusion, calibration |
| Robustness / OOD | Phase 8 suites |
| Quality / TEVV | Phases 2–5 guide tests; Phase 16 consolidation |
| Risk tracking | Risk register residual + acceptance |

## Manage

| Outcome | Project control |
|---|---|
| Risk response | Treat / mitigate / accept with owner + expiry |
| Monitoring | SLOs, auth failures, 4xx/5xx, model/version drift (Phases 14–17) |
| Response / rollback | Model bundle + signed image rollback via Argo |
| Retirement | Model and service retirement criteria in risk/quality policies |

## Traceability to releases

| Release | Primary AI RMF emphasis |
|---|---|
| 0 | Govern + Map framing |
| A | Map (data/model) + baseline Measure |
| B | Expanded Measure + Manage gate for champion/bundle |
| C–D | Security/ops controls enabling Manage in deployment |
| E | Full Manage / ORR / acceptance — confirmed `docs/evidence/release-e/ai_rmf_manage_confirmation.md` (2026-08-02) |
