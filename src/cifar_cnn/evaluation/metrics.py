"""Guide Step 5: evaluate accuracy on the locked CIFAR-10 test set."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import torch
import torch.nn as nn
from torch.utils.data import DataLoader

from cifar_cnn.data.constants import TEST_SIZE


@dataclass(frozen=True)
class EvalResult:
    total: int
    correct: int
    accuracy_pct: float
    avg_loss: float | None = None
    message: str = ""


def evaluate_accuracy(
    model: nn.Module,
    testloader: DataLoader[Any],
    *,
    device: str | torch.device = "cpu",
    criterion: nn.Module | None = None,
    expected_total: int | None = TEST_SIZE,
) -> EvalResult:
    """Run guide eval: ``no_grad``, ``torch.max(outputs, 1)``, full test coverage."""
    device = torch.device(device)
    model = model.to(device)
    model.eval()
    correct = 0
    total = 0
    loss_sum = 0.0
    loss_batches = 0

    with torch.no_grad():
        for images, labels in testloader:
            images = images.to(device)
            labels = labels.to(device)
            outputs = model(images)
            _, predicted = torch.max(outputs, 1)
            total += int(labels.size(0))
            correct += int((predicted == labels).sum().item())
            if criterion is not None:
                loss_sum += float(criterion(outputs, labels).item())
                loss_batches += 1

    if expected_total is not None and total != expected_total:
        raise ValueError(
            f"Expected exactly {expected_total} test predictions; got {total}"
        )

    accuracy_pct = 100.0 * correct / total if total else 0.0
    avg_loss = (loss_sum / loss_batches) if loss_batches else None
    message = (
        f"Accuracy of the network on {total} test images: {accuracy_pct:.2f}%"
    )
    return EvalResult(
        total=total,
        correct=correct,
        accuracy_pct=accuracy_pct,
        avg_loss=avg_loss,
        message=message,
    )


def write_metrics(
    path: str | Path,
    result: EvalResult,
    extra: dict[str, Any] | None = None,
) -> Path:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    payload: dict[str, Any] = asdict(result)
    payload["guide_line"] = result.message
    payload["official_test_locked"] = True
    payload["non_production"] = True
    if extra:
        payload.update(extra)
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return out
