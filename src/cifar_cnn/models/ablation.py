"""Short ablation protocol: baseline / aug-only / reg-only / combined."""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms

from cifar_cnn.models.improved_cnn import ImprovedCNN
from cifar_cnn.models.simple_cnn import SimpleCNN
from cifar_cnn.training.controlled import seed_everything
from cifar_cnn.training.trainer import build_criterion, build_optimizer, train_step


@dataclass(frozen=True)
class AblationVariant:
    name: str
    model_factory: str  # simple | improved
    batch_norm: bool
    dropout: bool
    train_augment: bool


ABLATION_VARIANTS: tuple[AblationVariant, ...] = (
    AblationVariant("baseline", "simple", False, False, False),
    AblationVariant("aug_only", "simple", False, False, True),
    AblationVariant("reg_only", "improved", True, True, False),
    AblationVariant("combined", "improved", True, True, True),
)


class TensorTrainAugmentDataset(Dataset[Any]):
    """Apply crop/flip to tensor samples for FakeCIFAR-style ablation smoke."""

    def __init__(self, base: Dataset[Any], *, augment: bool) -> None:
        self.base = base
        self.augment = augment
        self._aug = transforms.Compose(
            [
                transforms.RandomCrop(32, padding=4),
                transforms.RandomHorizontalFlip(),
            ]
        )

    def __len__(self) -> int:
        return len(self.base)  # type: ignore[arg-type]

    def __getitem__(self, index: int) -> tuple[torch.Tensor, Any]:
        image, label = self.base[index]
        if self.augment:
            image = self._aug(image)
        return image, label


def build_variant_model(variant: AblationVariant) -> nn.Module:
    if variant.model_factory == "simple":
        return SimpleCNN()
    return ImprovedCNN(batch_norm=variant.batch_norm, dropout=variant.dropout)


@dataclass
class AblationRunResult:
    name: str
    train_augment: bool
    batch_norm: bool
    dropout: bool
    final_train_loss: float
    final_eval_loss: float
    loss_curve: list[float]


@torch.no_grad()
def _eval_loss(
    model: nn.Module, loader: DataLoader[Any], criterion: nn.Module, device: torch.device
) -> float:
    model.eval()
    total = 0.0
    n = 0
    for images, labels in loader:
        images = images.to(device)
        labels = labels.to(device)
        loss = criterion(model(images), labels)
        total += float(loss.item()) * int(labels.size(0))
        n += int(labels.size(0))
    return total / n if n else float("inf")


def run_ablation_variant(
    variant: AblationVariant,
    trainloader: DataLoader[Any],
    evalloader: DataLoader[Any],
    *,
    seed: int = 42,
    epochs: int = 2,
    max_batches: int = 4,
    device: str = "cpu",
) -> AblationRunResult:
    """Run a short comparable protocol for one ablation arm."""
    seed_everything(seed)
    model = build_variant_model(variant).to(device)
    criterion = build_criterion()
    optimizer = build_optimizer(model, lr=0.001)
    device_t = torch.device(device)
    curve: list[float] = []

    for _epoch in range(epochs):
        model.train()
        running = 0.0
        seen = 0
        for i, batch in enumerate(trainloader):
            if i >= max_batches:
                break
            running += train_step(model, batch, criterion, optimizer, device_t)
            seen += 1
        curve.append(running / max(seen, 1))

    eval_loss = _eval_loss(model, evalloader, criterion, device_t)
    return AblationRunResult(
        name=variant.name,
        train_augment=variant.train_augment,
        batch_norm=variant.batch_norm,
        dropout=variant.dropout,
        final_train_loss=curve[-1] if curve else float("inf"),
        final_eval_loss=eval_loss,
        loss_curve=curve,
    )


def run_ablation_suite(
    make_loaders: Callable[[bool], tuple[DataLoader[Any], DataLoader[Any]]],
    *,
    seed: int = 42,
    epochs: int = 2,
    max_batches: int = 4,
) -> list[AblationRunResult]:
    """``make_loaders(train_augment)`` must keep eval loader unaugmented."""
    results: list[AblationRunResult] = []
    for variant in ABLATION_VARIANTS:
        trainloader, evalloader = make_loaders(variant.train_augment)
        results.append(
            run_ablation_variant(
                variant,
                trainloader,
                evalloader,
                seed=seed,
                epochs=epochs,
                max_batches=max_batches,
            )
        )
    return results


def write_ablation_report(
    path: str | Path,
    results: list[AblationRunResult],
    *,
    extra: dict[str, Any] | None = None,
) -> Path:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    payload: dict[str, Any] = {
        "protocol": {
            "seeds": "fixed per suite",
            "optimizer": "Adam(lr=0.001)",
            "loss": "CrossEntropyLoss",
            "eval_augmented": False,
            "variants": [asdict(v) for v in ABLATION_VARIANTS],
        },
        "results": [asdict(r) for r in results],
        "residual_risk": (
            "Short smoke ablations on synthetic/FakeCIFAR do not prove real-world "
            "generalization; overfitting risk remains (AIR-03)."
        ),
    }
    if extra:
        payload.update(extra)
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return out
