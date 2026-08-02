"""ResNet18 transfer candidate for CIFAR-10 (Release B)."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Literal, cast

import torch
import torch.nn as nn
from torchvision.models import ResNet18_Weights, resnet18

FreezeMode = Literal["none", "backbone", "all_but_fc"]


@dataclass(frozen=True)
class TransferProvenance:
    architecture: str
    weights_name: str
    weights_url: str | None
    license_note: str
    preprocessing: str
    classifier: str
    freeze_mode: FreezeMode
    adapted_for_cifar: bool


PROVENANCE_PRETRAINED = TransferProvenance(
    architecture="torchvision.models.resnet18",
    weights_name="ResNet18_Weights.IMAGENET1K_V1",
    weights_url="https://download.pytorch.org/models/resnet18-f37072fd.pth",
    license_note=(
        "Torchvision model code is BSD-3-Clause. ImageNet-1K pretrained weights are "
        "redistributed by the PyTorch project for research/education; review current "
        "torchvision weight license/terms before commercial redistribution. "
        "ImageNet itself has separate research-use terms."
    ),
    preprocessing=(
        "For transfer inputs: resize/crop to 224 and Normalize(ImageNet mean/std). "
        "CIFAR-adapted stem accepts 32x32; still prefer ImageNet normalization when "
        "loading IMAGENET1K_V1 weights."
    ),
    classifier="fc replaced with Linear(512, 10) for CIFAR-10 logits",
    freeze_mode="backbone",
    adapted_for_cifar=True,
)

PROVENANCE_SCRATCH = TransferProvenance(
    architecture="torchvision.models.resnet18",
    weights_name="None (random init; CI/smoke)",
    weights_url=None,
    license_note="Torchvision model code BSD-3-Clause; no pretrained weight download.",
    preprocessing="CIFAR-adapted 32x32 stem; guide or ImageNet normalize per config",
    classifier="fc replaced with Linear(512, 10)",
    freeze_mode="none",
    adapted_for_cifar=True,
)


def adapt_resnet18_for_cifar(model: nn.Module) -> nn.Module:
    """Use 3x3 stride-1 stem and drop the aggressive max-pool for 32x32 inputs."""
    model.conv1 = nn.Conv2d(3, 64, kernel_size=3, stride=1, padding=1, bias=False)
    model.maxpool = nn.Identity()
    fc = model.fc
    if not isinstance(fc, nn.Linear):
        raise TypeError("Expected Linear classifier head on ResNet")
    model.fc = nn.Linear(int(fc.in_features), 10)
    return model


def set_freeze_mode(model: nn.Module, mode: FreezeMode) -> None:
    if mode == "none":
        for p in model.parameters():
            p.requires_grad = True
        return
    # Freeze backbone; train classifier head only.
    for name, p in model.named_parameters():
        p.requires_grad = name.startswith("fc.")


def build_resnet18_cifar(
    *,
    pretrained: bool = False,
    freeze_mode: FreezeMode = "backbone",
) -> nn.Module:
    """Build CIFAR-oriented ResNet18; pretrained download is opt-in (not for PR CI)."""
    if pretrained:
        model = resnet18(weights=ResNet18_Weights.IMAGENET1K_V1)
    else:
        model = resnet18(weights=None)
    model = adapt_resnet18_for_cifar(model)
    if pretrained:
        # Stem no longer matches ImageNet conv1; re-init adapted stem.
        conv1 = model.conv1
        if not isinstance(conv1, nn.Conv2d):
            raise TypeError("Expected Conv2d stem after CIFAR adapt")
        nn.init.kaiming_normal_(conv1.weight, mode="fan_out", nonlinearity="relu")
        set_freeze_mode(model, freeze_mode)
    else:
        set_freeze_mode(model, "none")
    return cast(nn.Module, model)


def describe_transfer_stack(*, pretrained: bool, freeze_mode: FreezeMode) -> dict[str, Any]:
    base = PROVENANCE_PRETRAINED if pretrained else PROVENANCE_SCRATCH
    return {
        "architecture": base.architecture,
        "weights_name": base.weights_name,
        "weights_url": base.weights_url,
        "license_note": base.license_note,
        "preprocessing": base.preprocessing,
        "classifier": base.classifier,
        "freeze_mode": freeze_mode if pretrained else "none",
        "adapted_for_cifar": True,
        "input_shape": [3, 32, 32],
        "output": "logits",
        "supply_chain": {
            "source": "torchvision",
            "pin_recommendation": "torchvision==0.22.1 with torch==2.7.1",
            "hash_pin": "Record SHA-256 of downloaded .pth before fine-tune (offline)",
        },
    }


def count_trainable_parameters(model: nn.Module) -> int:
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


def estimate_state_dict_mb(model: nn.Module) -> float:
    nbytes = sum(v.numel() * v.element_size() for v in model.state_dict().values())
    return float(nbytes / (1024 * 1024))


@torch.no_grad()
def measure_cpu_latency_ms(
    model: nn.Module,
    *,
    batch_size: int = 1,
    warmup: int = 5,
    iters: int = 20,
) -> float:
    model.eval()
    x = torch.randn(batch_size, 3, 32, 32)
    for _ in range(warmup):
        model(x)
    t0 = time.perf_counter()
    for _ in range(iters):
        model(x)
    return float(1000.0 * (time.perf_counter() - t0) / iters)
