"""Expanded Measure metrics: confusion, P/R/F1, ROC/AUC, calibration."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch import Tensor
from torch.utils.data import DataLoader

from cifar_cnn.data.constants import CIFAR10_CLASSES, NUM_CLASSES


@dataclass
class PredictionBatch:
    logits: Tensor
    probs: Tensor
    preds: Tensor
    labels: Tensor


@dataclass
class ClassScores:
    precision: float
    recall: float
    f1: float
    support: int


@dataclass
class RigorousMetrics:
    accuracy: float
    avg_loss: float | None
    confusion: list[list[int]]
    per_class: dict[str, ClassScores]
    macro_precision: float
    macro_recall: float
    macro_f1: float
    weighted_precision: float
    weighted_recall: float
    weighted_f1: float
    roc_auc_macro: float | None
    ece: float
    n_samples: int
    class_names: tuple[str, ...] = CIFAR10_CLASSES
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["softmax_is_not_correctness"] = True
        payload["official_test_locked_for_tuning"] = True
        return payload


def collect_predictions(
    model: nn.Module,
    loader: DataLoader[Any],
    *,
    device: str | torch.device = "cpu",
    criterion: nn.Module | None = None,
    max_batches: int | None = None,
    tta_flip: bool = False,
) -> tuple[PredictionBatch, float | None]:
    """Collect logits/probs. Optional horizontal-flip TTA averages softmax probs."""
    device_t = torch.device(device)
    model = model.to(device_t)
    model.eval()
    logits_l: list[Tensor] = []
    probs_l: list[Tensor] = []
    labels_l: list[Tensor] = []
    loss_sum = 0.0
    loss_n = 0
    with torch.no_grad():
        for i, (images, labels) in enumerate(loader):
            if max_batches is not None and i >= max_batches:
                break
            images = images.to(device_t)
            labels = labels.to(device_t)
            outputs = model(images)
            probs = F.softmax(outputs, dim=1)
            if tta_flip:
                flipped = torch.flip(images, dims=[3])
                probs = 0.5 * (probs + F.softmax(model(flipped), dim=1))
                # Keep logits aligned to the averaged decision for reporting.
                outputs = torch.log(probs.clamp_min(1e-12))
            logits_l.append(outputs.cpu())
            probs_l.append(probs.cpu())
            labels_l.append(labels.cpu())
            if criterion is not None and not tta_flip:
                loss_sum += float(criterion(outputs, labels).item()) * int(labels.size(0))
                loss_n += int(labels.size(0))
    logits = torch.cat(logits_l, dim=0)
    labels_t = torch.cat(labels_l, dim=0)
    probs = torch.cat(probs_l, dim=0)
    preds = torch.argmax(probs, dim=1)
    avg_loss = (loss_sum / loss_n) if loss_n else None
    return PredictionBatch(logits=logits, probs=probs, preds=preds, labels=labels_t), avg_loss


def confusion_matrix(y_true: Tensor, y_pred: Tensor, num_classes: int = NUM_CLASSES) -> Tensor:
    cm = torch.zeros(num_classes, num_classes, dtype=torch.int64)
    for t, p in zip(y_true.view(-1).tolist(), y_pred.view(-1).tolist(), strict=True):
        cm[int(t), int(p)] += 1
    return cm


def per_class_prf(
    cm: Tensor, class_names: tuple[str, ...] = CIFAR10_CLASSES
) -> dict[str, ClassScores]:
    out: dict[str, ClassScores] = {}
    for i, name in enumerate(class_names):
        tp = float(cm[i, i].item())
        fp = float(cm[:, i].sum().item() - tp)
        fn = float(cm[i, :].sum().item() - tp)
        support = int(cm[i, :].sum().item())
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (
            2 * precision * recall / (precision + recall)
            if (precision + recall) > 0
            else 0.0
        )
        out[name] = ClassScores(precision, recall, f1, support)
    return out


def _aggregate(
    per_class: dict[str, ClassScores], *, weighted: bool
) -> tuple[float, float, float]:
    items = list(per_class.values())
    if not items:
        return 0.0, 0.0, 0.0
    if not weighted:
        n = len(items)
        return (
            sum(c.precision for c in items) / n,
            sum(c.recall for c in items) / n,
            sum(c.f1 for c in items) / n,
        )
    total = sum(c.support for c in items) or 1
    return (
        sum(c.precision * c.support for c in items) / total,
        sum(c.recall * c.support for c in items) / total,
        sum(c.f1 * c.support for c in items) / total,
    )


def binary_roc_auc(y_true: Tensor, y_score: Tensor) -> float | None:
    """Trapezoidal ROC-AUC for a binary label/score pair; None if undefined."""
    y = y_true.detach().cpu().double()
    s = y_score.detach().cpu().double()
    pos = int((y == 1).sum().item())
    neg = int((y == 0).sum().item())
    if pos == 0 or neg == 0:
        return None
    order = torch.argsort(s, descending=True)
    y_sorted = y[order]
    tps = torch.cumsum(y_sorted, dim=0)
    fps = torch.cumsum(1.0 - y_sorted, dim=0)
    tpr = tps / pos
    fpr = fps / neg
    # prepend origin
    tpr = torch.cat([torch.tensor([0.0]), tpr])
    fpr = torch.cat([torch.tensor([0.0]), fpr])
    return float(torch.trapezoid(tpr, fpr).item())


def multiclass_roc_auc_macro(y_true: Tensor, probs: Tensor) -> float | None:
    aucs: list[float] = []
    for k in range(probs.shape[1]):
        auc = binary_roc_auc((y_true == k).long(), probs[:, k])
        if auc is not None:
            aucs.append(auc)
    if not aucs:
        return None
    return float(sum(aucs) / len(aucs))


def expected_calibration_error(
    probs: Tensor, y_true: Tensor, *, n_bins: int = 10
) -> float:
    """ECE over max-softmax confidence (not a correctness proof)."""
    conf, pred = probs.max(dim=1)
    correct = (pred == y_true).float()
    ece = 0.0
    for b in range(n_bins):
        lo, hi = b / n_bins, (b + 1) / n_bins
        mask = (conf > lo) & (conf <= hi) if b > 0 else (conf >= lo) & (conf <= hi)
        if not bool(mask.any()):
            continue
        acc = float(correct[mask].mean().item())
        avg_conf = float(conf[mask].mean().item())
        ece += abs(acc - avg_conf) * (float(mask.sum().item()) / float(probs.shape[0]))
    return float(ece)


def compute_rigorous_metrics(
    batch: PredictionBatch,
    *,
    avg_loss: float | None = None,
    class_names: tuple[str, ...] = CIFAR10_CLASSES,
) -> RigorousMetrics:
    cm = confusion_matrix(batch.labels, batch.preds, num_classes=len(class_names))
    per = per_class_prf(cm, class_names)
    macro_p, macro_r, macro_f = _aggregate(per, weighted=False)
    weight_p, weight_r, weight_f = _aggregate(per, weighted=True)
    acc = float((batch.preds == batch.labels).float().mean().item())
    return RigorousMetrics(
        accuracy=acc,
        avg_loss=avg_loss,
        confusion=cm.tolist(),
        per_class=per,
        macro_precision=macro_p,
        macro_recall=macro_r,
        macro_f1=macro_f,
        weighted_precision=weight_p,
        weighted_recall=weight_r,
        weighted_f1=weight_f,
        roc_auc_macro=multiclass_roc_auc_macro(batch.labels, batch.probs),
        ece=expected_calibration_error(batch.probs, batch.labels),
        n_samples=int(batch.labels.numel()),
        class_names=class_names,
        notes=[
            "Softmax confidence is not proof of correctness.",
            "Official test set must not be used for hyperparameter tuning.",
        ],
    )


def write_rigorous_metrics(path: str | Path, metrics: RigorousMetrics) -> Path:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(metrics.to_dict(), indent=2) + "\n", encoding="utf-8")
    return out
