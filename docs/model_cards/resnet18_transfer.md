# Model Card — ResNet18 Transfer Candidate (Release B)

| Field | Value |
|---|---|
| Name | ResNet18CIFAR |
| Status | Candidate — selection via val-only rule |
| Pretrained weights | `ResNet18_Weights.IMAGENET1K_V1` (offline opt-in) |
| CI/smoke | `pretrained=false` random init, same adapted architecture |

## Architecture adaptations

- `conv1`: 3×3, stride 1, padding 1 (CIFAR stem)
- `maxpool`: Identity
- `fc`: `Linear(512, 10)` logits

## Provenance / supply chain

| Item | Detail |
|---|---|
| Code | `torchvision.models.resnet18` (BSD-3-Clause) |
| Weights URL | `https://download.pytorch.org/models/resnet18-f37072fd.pth` |
| License | Review current torchvision/ImageNet weight terms before commercial use |
| Hash pin | Record SHA-256 of downloaded weights before fine-tune (offline) |
| Pins | `torch==2.7.1`, `torchvision==0.22.1` |

## Freeze / fine-tune

Default offline recipe: freeze backbone (`requires_grad=False` except `fc`), Adam on classifier, then optional unfreeze. Smoke path trains all randomly-initialized layers briefly for protocol tests only.

## Non-claims

- Smoke FakeCIFAR comparisons are **not** ImageNet-transfer performance claims.
- Official CIFAR-10 test set is **not** used for champion selection.
