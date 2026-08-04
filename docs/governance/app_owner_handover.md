# App Owner Handover — CIFAR-10 CNN Classification Platform

| Field | Value |
|---|---|
| Document type | Application Owner Handover |
| System | CIFAR-10 CNN image classification platform |
| Version | 1.0 |
| Date | 2026-08-04 |
| Primary owner (current) | koenchill |
| Status | Active — Releases A–E complete; live model uplift in progress |
| Related | `docs/architecture/technical_design_document.md`, `docs/governance/raci.md`, `docs/evidence/leadership_brief_cifar_cnn_revD.docx` |

---

## 1. Purpose of this handover

This document transfers operational and ownership context for the CIFAR-10 CNN platform so a successor App Owner (or the same owner under expanded team roles) can:

1. Run, evaluate, and package models safely.
2. Operate the FastAPI service and understand security controls.
3. Promote changes through Git → CI → GitOps without breaking branch protection.
4. Know current model quality, accepted risks, and open follow-ups (Colab GPU transfer).

---

## 2. System at a glance

**What it is:** An educational / reference enterprise stack that trains CNN classifiers on CIFAR-10 (60k images: 50k train / 10k locked test), evaluates them rigorously, packages bundles, and serves authenticated predictions via FastAPI — optionally on hardened Docker and AWS EKS + Argo CD.

**What it is not:** A production vision system for arbitrary real-world photos, medical, biometric, or safety-critical decisions. See `docs/governance/intended_use.md`.

**Delivery status:** Implementation phases 00–17 marked **done** (`docs/implementation/STATUS.md`). Release E ORR package exists under `docs/evidence/release-e/`.

---

## 3. Ownership and RACI

Canonical RACI: `docs/governance/raci.md`.

| Role | Current assignee | App Owner must |
|---|---|---|
| AI system owner | koenchill | Approve intended use and release decisions |
| Application owner | koenchill | Own FastAPI boundary, serve configs, API SLOs |
| Model owner | koenchill | Champion selection, training recipes, model cards |
| Data owner | koenchill | Split manifests, leakage controls |
| Platform owner | koenchill | Terraform / EKS / Argo |
| Security owner | koenchill | Threat model, scanning, IAM |
| SRE / ops | koenchill | Runbooks, incidents, rollback |

**Separation of duties** is aspirational while single-owner; required for production promotion evidence (Phase 17).

---

## 4. Current model & metrics (locked 10k test)

| Recipe | Accuracy | Macro P | Macro R | Macro F1 | ROC-AUC | Artifact |
|---|---:|---:|---:|---:|---:|---|
| Baseline SimpleCNN | 73.4% | 0.740 | 0.734 | 0.736 | 0.963 | `artifacts/baseline_rigorous/` |
| ImprovedCNN (prior) | 78.5% | 0.783 | 0.785 | 0.783 | 0.976 | `artifacts/improved_full_rigorous_latest/` |
| ImprovedCNN boost | 80.8% | 0.807 | 0.808 | 0.806 | 0.979 | `artifacts/improved_boost_rigorous/` |
| **Boost + TTA (CPU champion)** | **81.8%** | **0.817** | **0.818** | **0.817** | **0.981** | `artifacts/improved_boost_rigorous_tta/` |
| ResNet18 Colab GPU transfer | Pending | — | — | — | — | Needs `artifacts/transfer_live/model_best.pth` |

**CPU champion checkpoint:** `artifacts/improved_boost/model_best.pth`  
**Default served bundle (image):** `models/bundles/simple_cnn-1.0.1` (guide SimpleCNN lineage — **not** yet the boost champion).  
**Phase-9 formal smoke champion** (FakeCIFAR protocol only): SimpleCNN — not a live CIFAR claim (`docs/evidence/release-b/phase-09-champion-decision.json`).

**Weak classes (boost+TTA):** cat (low recall), bird. Strong: automobile, ship, truck.

---

## 5. Day-1 checklist (new App Owner)

1. [ ] Read `docs/governance/intended_use.md` and `docs/governance/risk_acceptance_release_e.md`.
2. [ ] Clone repo; use Python 3.11; `pip install -e ".[dev]"`; `pre-commit install`.
3. [ ] Confirm local GPU reality: this portfolio workstation is **AMD Radeon 780M** — **CUDA unavailable**. Use Colab for ResNet GPU training.
4. [ ] Run smoke: `python scripts/train_controlled.py --smoke`.
5. [ ] Re-eval CPU champion:
   ```bash
   python scripts/evaluate_rigorous.py --live --model ImprovedCNN \
     --checkpoint artifacts/improved_boost/model_best.pth \
     --out-dir artifacts/improved_boost_rigorous_tta --tta
   ```
6. [ ] Bring up API locally: `docker compose -f deploy/docker/compose.yaml up --build` → `http://localhost:8000/health`.
7. [ ] Review required CI checks and branch protection (`docs/governance/branch_protection.md`).
8. [ ] Locate runbooks under `docs/runbooks/` (incident, GitOps promote/rollback).

---

## 6. How to operate — common commands

### 6.1 Training

| Goal | Command |
|---|---|
| Guide baseline | `python scripts/train.py --config configs/train/baseline.yaml` |
| Controlled / improved | `python scripts/train_controlled.py --config configs/train/improved_boost.yaml --live` |
| GPU transfer (NVIDIA only) | `python scripts/train_transfer_live.py --device cuda` |
| Colab | `notebooks/colab_transfer_gpu.ipynb` with `BRANCH=feature/live-rigorous-metrics-roc` |

Configs: `configs/train/*.yaml`. Split manifest: `data/splits/split_manifest.json` (45k/5k val, seed 42). Official test never used for tuning.

### 6.2 Evaluation

```bash
python scripts/evaluate_rigorous.py --live --model ImprovedCNN \
  --checkpoint <path.pth> --out-dir artifacts/<run> [--tta]

# After Colab ResNet download:
python scripts/evaluate_rigorous.py --live --model ResNet18CIFAR \
  --normalize imagenet --checkpoint artifacts/transfer_live/model_best.pth \
  --out-dir artifacts/transfer_rigorous --tta
```

### 6.3 Serving

```bash
uvicorn cifar_cnn.api.app:app_factory --factory --host 0.0.0.0 --port 8000
# or
docker compose -f deploy/docker/compose.yaml up --build
```

| Endpoint | Auth | Notes |
|---|---|---|
| `GET /health` | No | Liveness |
| `GET /ready` | No | Readiness |
| `GET /v1/metadata` | Yes | Model metadata |
| `POST /v1/predict` | Yes | Image upload; rate limited; audited |

Serve configs: `configs/serve/api.dev.yaml`, `api.prod.yaml`.  
Env template: `.env.example`.

### 6.4 Packaging / champion

```bash
python scripts/select_champion.py   # val-only protocol
python scripts/pack_bundle.py
```

---

## 7. Repository map (owner view)

| Path | Own as App Owner? | Notes |
|---|---|---|
| `src/cifar_cnn/api/` | **Primary** | FastAPI app factory, auth, predict |
| `configs/serve/` | **Primary** | Dev/prod API knobs |
| `deploy/docker/` | Shared w/ Platform | Image used to serve |
| `deploy/kustomize/`, `deploy/argocd/` | Shared w/ Platform | Desired state |
| `src/cifar_cnn/training/`, `models/` | Consult Model owner | Training & architectures |
| `docs/runbooks/` | Shared w/ SRE | Ops procedures |
| `docs/governance/` | Shared w/ AI/Security | Policy & risk |

Full layout: `README.md`, `docs/implementation/PATH_MAP.md`.

---

## 8. Security controls you inherit

| Control | Where |
|---|---|
| OIDC JWT + deny-by-default RBAC | `docs/architecture/api_security.md` |
| No long-lived AWS keys in PR CI | `docs/architecture/ci_oidc_trust.md` |
| SAST / SCA / DAST required on PR | `.github/workflows/ci-security.yml` |
| SCA allowlist | `security/sca-allowlist.txt` (CYB-08) |
| Secret scanning / pre-commit | repo hooks |
| Image signing / digest promotion | Docker envelope + GitOps scripts |
| Upload size / rate limits / audit (no image bytes in logs) | API layer |

**Do not:** disable auth in prod; log tokens or raw images; claim “NIST certified.”

---

## 9. Accepted risks (must acknowledge)

From `docs/governance/risk_register.md` and `risk_acceptance_release_e.md`:

| ID | Theme | Owner stance |
|---|---|---|
| AIR-01 | Over-trust CIFAR accuracy on real photos | Accepted Rel E — document prohibited uses |
| AIR-05 | High-confidence OOD errors | Accepted with API controls |
| CYB-07 | Torch pin advisories | Accepted → reassess by 2026-11-01 |
| CYB-08 | Transitive CVE backlog | Accepted via SCA allowlist |

App Owner must not expand intended use without risk re-review.

---

## 10. CI / branching / promotion

```text
feature/<topic>  →  PR (+ required checks)  →  dev  →  PR  →  main
```

**Required checks (strict):** `lint-test`, `iam-negative-guard`, PR title, `sast`, `sca`, `dast`.

**Prod changes:** reviewed PR updating Kustomize/Argo desired state; Argo reconciles. No routine laptop `kubectl apply` to prod.

See `CONTRIBUTING.md`, `docs/governance/branch_protection.md`, `docs/runbooks/gitops-promotion.md`, `gitops-rollback.md`.

**Active feature branch for GPU/boost work:** `feature/live-rigorous-metrics-roc` (includes `train_transfer_live.py` and Colab notebook).

---

## 11. Deploy topology (optional AWS path)

```text
Developer → GitHub PR/CI → GHCR image (digest)
                         → Argo CD Application
                         → EKS (Kustomize overlay)
```

| Layer | Path |
|---|---|
| Dockerfile | `deploy/docker/Dockerfile` (CPU torch serve image) |
| Compose | `deploy/docker/compose.yaml` |
| Kustomize | `deploy/kustomize/base`, `overlays/{dev,staging,prod}` |
| Argo CD | `deploy/argocd/applications/` |
| Terraform | `infra/terraform/envs/{dev,staging,prod}`, `modules/` |

ORR: `docs/evidence/release-e/orr_package.md`, `deploy/orr/`.

---

## 12. Open follow-ups (handover debt)

1. **Complete Colab ResNet18 transfer**, download real `model_best.pth` (not `.ipynb`), run locked-test eval, update leadership brief Rev E.
2. **Decide whether to re-bundle/serve** ImprovedCNN boost (or future ResNet) vs current `simple_cnn-1.0.1` image default.
3. **Reassess CYB-07/08** before any public production claim (expiry 2026-11-01).
4. Merge `feature/live-rigorous-metrics-roc` → `dev` via PR when ready.
5. Keep educational / non-production positioning in all external demos.

---

## 13. Incident & support pointers

| Situation | Start here |
|---|---|
| API down / bad deploy | `docs/runbooks/k8s-rollout.md`, `gitops-rollback.md` |
| Security incident | `docs/runbooks/incident-response.md` |
| Alert fire | `docs/runbooks/alert-response.md` |
| Vulnerability | `docs/runbooks/vulnerability-lifecycle.md` |
| Continuity | `docs/runbooks/continuity-restore.md` |

---

## 14. Handover acceptance

| Item | Sign-off |
|---|---|
| Intended use & prohibited uses understood | ________ / date |
| Risk acceptances (AIR-01, AIR-05, CYB-07/08) acknowledged | ________ / date |
| Day-1 checklist completed | ________ / date |
| CPU champion metrics & checkpoint known | ________ / date |
| Colab GPU follow-up ownership assigned | ________ / date |
| Access to GitHub, GHCR, cloud (if any) confirmed | ________ / date |

**Outgoing App Owner:** __________________  
**Incoming App Owner:** __________________  
**Date:** __________________
