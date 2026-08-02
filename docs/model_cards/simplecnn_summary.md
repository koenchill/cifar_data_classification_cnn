# Model Summary — SimpleCNN (guide baseline)

| Field | Value |
|---|---|
| Name | SimpleCNN |
| Phase | 3 |
| Status | Architecture locked for Release A baseline |
| Owner | Model owner (`koenchill`) |

## Architecture (guide Step 2)

| Layer | Spec |
|---|---|
| `conv1` | `Conv2d(3, 32, 3, padding=1)` → ReLU → MaxPool2d(2,2) |
| `conv2` | `Conv2d(32, 64, 3, padding=1)` → ReLU → MaxPool2d(2,2) |
| `conv3` | `Conv2d(64, 64, 3, padding=1)` → ReLU → MaxPool2d(2,2) |
| Flatten | `64 * 4 * 4` = 1024 |
| `fc1` | `Linear(1024, 64)` → ReLU |
| `fc2` | `Linear(64, 10)` logits (no softmax) |

## Parameter count

Documented by `count_parameters(SimpleCNN())` in integrity tests (see Phase 03 gate).

## Trusted artifacts

- **Allowed:** `state_dict` saved with `torch.save(model.state_dict(), …)` by this application (`.pth`).
- **Load policy:** Prefer `torch.load(..., weights_only=True)`; optional SHA-256 pin; refuse non-dict / hash-mismatched files (fail closed).
- **Forbidden:** Arbitrary pickle object graphs, untrusted third-party pickles, architecture substitutions (BN/Dropout/ResNet) on the baseline path.

## Limitations

Educational CIFAR-10 baseline only. Not a production vision system; see intended-use and data card.
