# Model Card — Guide Baseline SimpleCNN (Release A)

| Field | Value |
|---|---|
| Model | SimpleCNN (student guide Steps 2–7) |
| Dataset | CIFAR-10 (official 10k test locked) |
| Owner | `koenchill` |
| Status | Educational baseline — guide contract locked; production serving uses governed bundle + API controls (Release E ORR) |
| Training | `CrossEntropyLoss`, `Adam(lr=0.001)`, 10 epochs, batch 32 |

## Intended use

- Teaching CNN training/evaluation/visualization/persistence on CIFAR-10.
- Traceable evidence for Release A guide compliance.

## Out of scope

- Real-world safety, medical, automotive, or compliance decisions.
- Claims of state-of-the-art accuracy or robustness.
- Using the official test set for hyperparameter tuning.

## Metrics

Accuracy on **10,000** official (or FakeCIFAR-equivalent) test images, reported as  
`Accuracy of the network on 10000 test images: {pct}%`.  
Optional additive: average test cross-entropy loss.

Evidence artifacts:

- `docs/evidence/release-a/baseline_metrics.json` (smoke/FakeCIFAR or live run)
- `docs/evidence/release-a/baseline_gallery.png` (8 images, Actual/Predicted)

## Artifacts

| Path | Role |
|---|---|
| `models/cnn_model.pth` | Repo-canonical `state_dict` |
| `cnn_model.pth` (repo root) | Guide-literal path (gitignored) |

Load with application helper (`weights_only` when available); optional SHA-256 pin.

## Ethical / risk notes

CIFAR-10 labels are coarse and dataset-biased. Do not deploy this checkpoint for people-impacting decisions. Document limitations in learning evidence (`learning_why_image_classification.md`).
