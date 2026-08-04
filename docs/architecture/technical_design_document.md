# Technical Design Document — CIFAR-10 CNN Classification Platform

| Field | Value |
|---|---|
| Document type | Technical Design Document (TDD) |
| System | CIFAR-10 CNN train → evaluate → package → serve |
| Version | 1.0 |
| Date | 2026-08-04 |
| Status | As-built (Releases A–E) + live uplift path |
| Companion | `docs/governance/app_owner_handover.md` |
| Non-claim | Mapped to selected NIST AI RMF outcomes — **not** NIST certification |

---

## 1. Goals and non-goals

### 1.1 Goals

1. Deliver a **guide-compliant** CIFAR-10 `SimpleCNN` baseline (Release A).
2. Add **training controls**, improved models, rigorous metrics, transfer learning, and champion/bundle gates (Release B).
3. Expose **authenticated inference** via FastAPI with enterprise hardening (Release C).
4. Provide a **reference deploy path**: hardened Docker, optional AWS VPC/EKS (Terraform), GitOps (Argo CD) (Releases C–E).
5. Preserve **evaluation integrity**: official 10k test locked for reporting; tune on train/val only.

### 1.2 Non-goals

- Multi-tenant SaaS, billing, or customer private datasets.
- Real-time video, detection, or segmentation.
- Guaranteeing accuracy on non-CIFAR real-world photos.
- GPU-backed **serving** image (serve path is CPU torch by design).

---

## 2. System context

```text
[Developer workstation / Colab GPU]
        | train / eval (offline)
        v
[src/cifar_cnn + configs] --> [artifacts / models / bundles]
                                      |
                                      v
[Authenticated client] --OIDC--> [FastAPI /v1/*] --load--> [model bundle]
                                      |
                     +----------------+----------------+
                     v                                 v
              [Audit / metrics]                 [OIDC IdP]
                     |
                     v
        [Docker] -> [EKS via Argo CD] -> [AWS: VPC, IAM, ECR, logs]
```

Details: `docs/architecture/system_context.md`, `threat_model.md`, `aws_platform.md`.

**Trust boundaries:** offline training hosts; CI (untrusted PR code); container runtime; EKS data plane; IdP; artifact registries (GHCR/ECR).

---

## 3. Logical architecture

| Layer | Package / path | Responsibility |
|---|---|---|
| Data | `src/cifar_cnn/data/` | CIFAR-10 loaders, transforms, stratified splits |
| Models | `src/cifar_cnn/models/` | SimpleCNN, ImprovedCNN, ResNet18CIFAR |
| Training | `src/cifar_cnn/training/` | Loops, checkpoints, schedulers, tracking, authz |
| Evaluation | `src/cifar_cnn/evaluation/` | Accuracy, P/R/F1, ROC, ECE, plots, TTA, Grad-CAM |
| Inference | `src/cifar_cnn/inference/` | Bundle load, predict helpers, ONNX hooks |
| API | `src/cifar_cnn/api/` | FastAPI factory, authz, predict, health |
| CLIs | `scripts/` | Thin orchestration over library code |
| Config | `configs/{data,model,train,serve,experiments}/` | Declarative recipes |
| Deploy | `deploy/{docker,kustomize,argocd}/` | Image + desired state |
| Infra | `infra/terraform/` | AWS bootstrap + env stacks |

---

## 4. Data design

### 4.1 Dataset

- **CIFAR-10:** 60,000 RGB 32×32 images, 10 classes.
- **Official split:** 50,000 train / 10,000 test (`train=False` locked).
- **Local root:** `./data` (raw batches gitignored).

### 4.2 Train/validation protocol

- Manifest: `data/splits/split_manifest.json`
- Stratified **45,000 / 5,000** from the **training pool only** (seed 42).
- Official test indices never enter training or hyperparameter search.
- Enforcement helpers: `assert_official_test_locked`, contract tests.

### 4.3 Transforms

| Mode | Pipeline |
|---|---|
| Guide / eval | `ToTensor` + `Normalize(0.5)` |
| Train aug (boost) | RandomCrop+pad, Flip, optional ColorJitter, ToTensor, RandomErasing (Cutout), Normalize |
| Transfer | Same spatial aug family with **ImageNet** mean/std when using pretrained ResNet |

Eval/test loaders **never** apply train augmentation (except optional **TTA at inference**, which averages predictions and does not mutate labels).

---

## 5. Model design

### 5.1 SimpleCNN (Release A baseline)

- Conv path 3→32→64→64 with max-pool; MLP 1024→64→10 logits.
- Guide topology; baseline live accuracy ≈ **73.4%** on locked test.

### 5.2 ImprovedCNN (Release B / live CPU champion)

- Same spatial topology + optional BatchNorm after convs + Dropout on MLP.
- Boost recipe (`configs/train/improved_boost.yaml`):
  - Cutout / RandomErasing, color jitter
  - AdamW + weight decay
  - Label smoothing
  - CosineAnnealingLR
  - Warm-start via `init_weights` from prior best
- Locked-test: **80.8%**; with horizontal-flip TTA: **81.8%**.

### 5.3 ResNet18CIFAR (transfer)

- Torchvision ResNet18 adapted for CIFAR: 3×3 stride-1 stem, no aggressive max-pool; FC→10.
- Pretrained ImageNet weights optional (offline / Colab).
- Freeze modes: `backbone` (stage 1) → `none` (stage 2).
- Orchestration: `scripts/train_transfer_live.py --device {auto,cpu,cuda}`.
- GPU configs: `configs/train/transfer_stage{1,2}_gpu.yaml`.
- **Compute note:** Primary workstation is AMD Radeon 780M (no CUDA). GPU training is designed for **Google Colab** (`notebooks/colab_transfer_gpu.ipynb`) or other NVIDIA hosts. Target ≈ **90%+** locked-test accuracy pending completed run.

### 5.4 Champion & bundle

- Val-only selection rule: `configs/model/champion_selection.yaml`, `scripts/select_champion.py`.
- Bundle pack: `scripts/pack_bundle.py` → `models/bundles/`.
- Default image bundle remains guide SimpleCNN (`simple_cnn-1.0.1`) unless explicitly promoted.

---

## 6. Training subsystem design

### 6.1 Controlled training loop

`controlled_train_loop` (`src/cifar_cnn/training/controlled.py`):

- Seeded RNG / optional deterministic CuDNN flags
- Optimizer: Adam | AdamW | SGD (trainable params only)
- Scheduler: `step` | `cosine` | `none`
- Early stop on **validation loss**
- Atomic last/best checkpoints (`checkpoint_{last,best}.pt`)
- Artifact write authorization by identity (`training` / `eval` / `release`)
- JSONL/CSV/log tracking + optional TensorBoard stub

### 6.2 Config schema

`ControlledTrainConfig` loads known YAML keys only (fail-closed validation): model, aug flags, cutout, normalize, optimizer, weight_decay, label_smoothing, scheduler_*, device, init_weights vs resume_from exclusivity, etc.

### 6.3 CLIs

| Script | Role |
|---|---|
| `scripts/train.py` | Guide baseline |
| `scripts/train_controlled.py` | Controlled / improved / `--device` override |
| `scripts/train_transfer_live.py` | Two-stage ResNet; auto GPU YAML when `--device cuda` |

---

## 7. Evaluation subsystem design

### 7.1 Metrics

`compute_rigorous_metrics` produces:

- Top-1 accuracy, avg CE loss (when applicable)
- Confusion matrix
- Per-class / macro / weighted precision, recall, F1
- Macro one-vs-rest ROC-AUC
- ECE (max-softmax confidence — not a correctness proof)

Plots: confusion heatmap, OvR ROC curves (`src/cifar_cnn/evaluation/plots.py`).

### 7.2 TTA

`collect_predictions(..., tta_flip=True)` averages softmax of image and horizontal flip. CLI: `--tta` on `evaluate_rigorous.py`.

### 7.3 Leakage policy

- Tuning: val split only.
- Reporting: official test once per candidate.
- Missing transfer checkpoint yields actionable error (points to Colab / CPU champion).

---

## 8. API design

### 8.1 Entry

- Factory: `cifar_cnn.api.app:app_factory`
- Port: **8000** (compose and container); Service port 80→8000 in K8s.

### 8.2 Endpoints

| Method | Path | Auth | Purpose |
|---|---|---|---|
| GET | `/health` | No | Liveness |
| GET | `/ready` | No | Readiness (model loaded) |
| GET | `/v1/metadata` | Yes | Model / bundle metadata |
| POST | `/v1/predict` | Yes | Classify uploaded image |

### 8.3 Security controls

- OIDC JWT validation (dev static HS256; prod JWKS)
- Deny-by-default RBAC
- Upload size / content constraints
- Rate limiting
- Structured audit **without** logging image bytes or bearer tokens

Design detail: `docs/architecture/api_security.md`.

---

## 9. Packaging and runtime envelope

### 9.1 Docker

- `deploy/docker/Dockerfile`: hardened, non-root, **CPU** torch for serve.
- Compose: `deploy/docker/compose.yaml` → host 8000.
- Digest-oriented promotion; CI image workflow pushes GHCR tags.

### 9.2 Kubernetes / GitOps

- Kustomize base + `dev` / `staging` / `prod` overlays.
- Argo CD Applications under `deploy/argocd/applications/`.
- Promotion via PR to desired state; Argo reconciles (no CI cluster-admin apply).

### 9.3 AWS (optional)

Terraform modules: network, EKS, ECR, KMS, GitHub OIDC IAM.  
Envs: `infra/terraform/envs/{dev,staging,prod}`.  
Trust: GitHub OIDC federation — no long-lived AWS keys in PR CI (`docs/architecture/ci_oidc_trust.md`).

---

## 10. CI/CD design

```text
feature/*  --PR-->  dev  --PR-->  main
              |            |
         required checks   promote GitOps desired state
```

| Workflow | Purpose |
|---|---|
| `ci-pr.yml` | lint, mypy, bandit, secrets, pytest, iam-negative-guard |
| `ci-security.yml` | SAST, SCA (+ allowlist), DAST (ZAP) |
| `ci-image.yml` | container build/push |
| `terraform.yml` | infra plan/apply on protected envs |
| `gitops-promote.yml` | digest promotion helpers |
| `pr-title.yml` | conventional titles |

Required on protected branches: `lint-test`, `iam-negative-guard`, title, `sast`, `sca`, `dast`.

---

## 11. Observability and operations

- Health/ready probes on API.
- Audit events for predict path.
- Runbooks: `docs/runbooks/` (rollout, rollback, incident, alerts, vulns, continuity).
- SLO policy: `docs/governance/slo_policy.md`.
- ORR / Release E evidence: `docs/evidence/release-e/`.

---

## 12. Security and threat model (summary)

High-level threats (see `threat_model.md`):

- Model/data tampering → hash/sign bundles; trusted state_dict load.
- Auth bypass → OIDC mandatory in prod; RBAC deny-by-default.
- DoS via uploads → size/timeouts.
- Supply chain → pin deps, SCA, image digests.
- Over-trust of CIFAR scores → intended use + AIR-01 acceptance.

Residual accepted risks: AIR-01, AIR-05, CYB-07, CYB-08 (with expiry/reassessment dates).

---

## 13. Key design decisions

| Decision | Rationale |
|---|---|
| Official test locked | Prevent leakage; credible reporting |
| Serve image CPU-only | Portable demos; training GPU is offline/Colab |
| Colab for ResNet GPU | Local AMD iGPU cannot run CUDA |
| Val-only champion rules | Fair model selection |
| Config-driven training | Reproducibility + evidence |
| GitOps over CI kubectl | Least privilege; auditable desired state |
| Educational scope | Avoid false safety claims |

---

## 14. Current as-built metrics (reference)

| Candidate | Accuracy | Macro F1 | ROC-AUC |
|---|---:|---:|---:|
| SimpleCNN baseline | 73.4% | 0.736 | 0.963 |
| ImprovedCNN boost | 80.8% | 0.806 | 0.979 |
| ImprovedCNN boost + TTA | **81.8%** | **0.817** | **0.981** |
| ResNet18 Colab transfer | Pending | Pending | Pending |

Evidence roots: `artifacts/*_rigorous*/summary.json`, leadership brief Rev D.

---

## 15. Future work (design backlog)

1. Land ResNet18 Colab weights; publish locked-test metrics; champion decision.
2. Optionally promote boost/ResNet bundle into serve image (separate release).
3. Cosine/OneCycle + stronger aug already partially on GPU YAMLs; extend MixUp/CutMix if needed.
4. Torch/CVE pin upgrades before CYB-07/08 expiry (2026-11-01).
5. Merge `feature/live-rigorous-metrics-roc` → `dev` when PR-ready.

---

## 16. Document control

| Version | Date | Notes |
|---|---|---|
| 1.0 | 2026-08-04 | As-built TDD aligned to Releases A–E + CPU boost + Colab GPU path |

**Authors / maintainers:** Platform & Model Engineering (koenchill)  
**Reviewers:** App Owner, Security Owner, Model Owner (see RACI)
