"""Plot helpers for rigorous evaluation evidence."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import torch
from torch import Tensor

from cifar_cnn.data.constants import CIFAR10_CLASSES
from cifar_cnn.evaluation.rigorous import binary_roc_auc


def save_confusion_heatmap(
    cm: list[list[int]] | Tensor,
    path: str | Path,
    *,
    class_names: tuple[str, ...] = CIFAR10_CLASSES,
) -> Path:
    mat = torch.tensor(cm) if not isinstance(cm, Tensor) else cm
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(7, 6))
    im = ax.imshow(mat.numpy(), cmap="Blues")
    ax.set_xticks(range(len(class_names)), class_names, rotation=45, ha="right")
    ax.set_yticks(range(len(class_names)), class_names)
    ax.set_xlabel("Predicted")
    ax.set_ylabel("Actual")
    ax.set_title("Confusion matrix (reporting only; not for tuning)")
    fig.colorbar(im, ax=ax, fraction=0.046)
    fig.tight_layout()
    fig.savefig(out, dpi=120)
    plt.close(fig)
    return out


def _roc_curve_points(y_true: Tensor, y_score: Tensor) -> tuple[Tensor, Tensor] | None:
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
    tpr = torch.cat([torch.tensor([0.0]), tps / pos])
    fpr = torch.cat([torch.tensor([0.0]), fps / neg])
    return fpr, tpr


def save_roc_curves(
    labels: Tensor,
    probs: Tensor,
    path: str | Path,
    *,
    class_names: tuple[str, ...] = CIFAR10_CLASSES,
) -> Path:
    """One-vs-rest ROC curves + macro AUC annotation (reporting only)."""
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(7.5, 6.5))
    aucs: list[float] = []
    for k, name in enumerate(class_names):
        pts = _roc_curve_points((labels == k).long(), probs[:, k])
        if pts is None:
            continue
        fpr, tpr = pts
        auc = binary_roc_auc((labels == k).long(), probs[:, k])
        if auc is not None:
            aucs.append(auc)
            ax.plot(fpr.numpy(), tpr.numpy(), lw=1.4, label=f"{name} (AUC={auc:.3f})")
        else:
            ax.plot(fpr.numpy(), tpr.numpy(), lw=1.4, label=name)
    ax.plot([0, 1], [0, 1], "k--", lw=1, label="chance")
    ax.set_xlim(0.0, 1.0)
    ax.set_ylim(0.0, 1.05)
    ax.set_xlabel("False positive rate")
    ax.set_ylabel("True positive rate")
    macro = sum(aucs) / len(aucs) if aucs else float("nan")
    ax.set_title(f"One-vs-rest ROC (macro AUC={macro:.3f}; reporting only)")
    ax.legend(fontsize=8, loc="lower right")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(out, dpi=130)
    plt.close(fig)
    return out
