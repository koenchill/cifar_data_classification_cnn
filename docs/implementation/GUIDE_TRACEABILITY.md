# Student Guide Traceability (Release A)

Source: *Comprehensive Guide to Image Classification Project for Students (With Hints)*.  
Enterprise phases **2–5** (plus Phase 1 tool pinning) must satisfy every row. Enhancements beyond the guide are marked **additive** and must not alter baseline behavior.

## Coverage matrix

| Guide § | Requirement | Exact contract | Phase | Evidence / test |
|---|---|---|---|---|
| 1 | Why image classification matters | Written learning note (CV foundation → detection/segmentation/GANs) | 5 | `docs/evidence/release-a/learning_why_image_classification.md` |
| 2 | Tools | VS Code + Python documented | 1 | README / secure-dev checklist |
| 2 | Libraries | `torch`, `torchvision`, `matplotlib` declared | 1 | `pyproject.toml` deps |
| 2 | Install | Reproducible install of those libs (lock + `pip install -e .` / equiv.) | 1 | install verify |
| 3.1 | Transforms | `Compose([ToTensor(), Normalize((0.5,0.5,0.5),(0.5,0.5,0.5))])` | 2 | `tests/unit/test_data_contract.py` ✅ |
| 3.1 | Train set | `CIFAR10(root=./data, train=True, download=True, transform=…)` | 2 | `loaders.py` + baseline.yaml ✅ |
| 3.1 | Test set | `CIFAR10(..., train=False, download=True, transform=…)` | 2 | `loaders.py` + baseline.yaml ✅ |
| 3.1 | Train loader | `batch_size=32`, `shuffle=True` | 2 | config + RandomSampler test ✅ |
| 3.1 | Test loader | `batch_size=32`, `shuffle=False` | 2 | config + SequentialSampler test ✅ |
| 3.1 | Sizes | 50,000 train / 10,000 test | 2 | fake + optional live size tests ✅ |
| 3.2 | `conv1` | `Conv2d(3, 32, 3, padding=1)` | 3 | `test_simple_cnn.py` ✅ |
| 3.2 | `pool` | `MaxPool2d(2, 2)` (shared) | 3 | `test_simple_cnn.py` ✅ |
| 3.2 | `conv2` | `Conv2d(32, 64, 3, padding=1)` | 3 | `test_simple_cnn.py` ✅ |
| 3.2 | `conv3` | `Conv2d(64, 64, 3, padding=1)` | 3 | `test_simple_cnn.py` ✅ |
| 3.2 | `fc1` | `Linear(64*4*4, 64)` i.e. `Linear(1024, 64)` | 3 | `test_simple_cnn.py` ✅ |
| 3.2 | `fc2` | `Linear(64, 10)` | 3 | `test_simple_cnn.py` ✅ |
| 3.2 | Forward | `pool(relu(conv1))` ×3 → `view(-1, 64*4*4)` → `relu(fc1)` → `fc2` (logits) | 3 | forward/shape tests ✅ |
| 3.3 | Loss | `nn.CrossEntropyLoss()` | 4 | trainer test |
| 3.3 | Optimizer | `optim.Adam(params, lr=0.001)` | 4 | trainer test |
| 3.4 | Epochs | `10` | 4 | baseline config |
| 3.4 | Step order | `zero_grad` → forward → loss → `backward` → `step` | 4 | unit step test |
| 3.4 | Loss print | Every 100 mini-batches; print epoch/batch/loss | 4 | log evidence |
| 3.4 | Guide bug fix | **Must** accumulate `running_loss += loss.item()` before print (guide omits this) | 4 | corrected-loop test |
| 3.5 | Eval mode | `torch.no_grad()`; use `torch.max(outputs, 1)` | 5 | eval test |
| 3.5 | Coverage | Exactly 10,000 test images | 5 | count assert |
| 3.5 | Metric | Report accuracy `%` on those 10,000 | 5 | metrics file |
| 3.6 | Unnormalize | `img / 2 + 0.5` then HWC display | 5 | viz helper test |
| 3.6 | Labels | Title with **Actual** and **Predicted** class names | 5 | gallery |
| 3.6 | Count | **8** test images | 5 | gallery |
| 3.6 | Classes | Official CIFAR-10 names (guide references `classes` undefined) | 2/5 | `CIFAR10_CLASSES` ✅ (Phase 2) |
| 3.7 | Persist | `torch.save(state_dict, …)` | 5 | save/load test |
| 3.7 | Path | Guide literal `cnn_model.pth`; repo path `models/cnn_model.pth` | 5 | both satisfied (see note) |
| 4 | Why project matters for DS | Written note (healthcare/auto/retail + advanced CV path) | 5 | learning evidence |
| 5 | Tough questions (20) | Answer all 20 from `guide_tough_questions_source.md` | 5 | `guide_questions.md` |

## Path note for Step 7

| Guide snippet | Repo gold-standard |
|---|---|
| `torch.save(net.state_dict(), 'cnn_model.pth')` | `models/cnn_model.pth` |

**Compliance rule:** baseline save writes `models/cnn_model.pth` and also writes/copies `cnn_model.pth` at repo root **or** documents a single canonical path with a guide-equivalence test that loads the same state dict. Prefer writing **both** during Phase 5 so literal guide and repo layout are satisfied. Root `cnn_model.pth` remains gitignored.

## Additive (allowed after guide contract locked)

| Additive | First allowed |
|---|---|
| Stratified train/val split (official test locked) | Phase 2 |
| Device transfer (CPU default; optional GPU) | Phase 4 |
| Eval loss in addition to accuracy | Phase 5 |
| Gallery confidence + correctness flags | Phase 5 |
| Seeded/reproducible runs, checkpoints | Phase 4–6 |
| BN/Dropout/aug/ResNet/ONNX/API/K8s | Phase 7+ |

## Guide defects to preserve awareness of

1. **Training snippet** prints `running_loss / 100` but never adds `loss.item()` — implement the corrected accumulation; document the guide defect in Phase 4 evidence.
2. **`classes`** is used in visualization but never defined — define official CIFAR-10 class tuple in data module.
3. **Tough questions** (20) are in `docs/evidence/release-a/guide_tough_questions_source.md`; Phase 5 must answer all of them in `guide_questions.md`.

## Release A exit (no gaps)

Release A is complete only when every **Requirement** row above is `done` in this matrix (update checkboxes in phase cards + this file’s evidence links).
