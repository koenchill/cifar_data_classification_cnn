"""Plot helpers for rigorous evaluation evidence."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import torch
from torch import Tensor

from cifar_cnn.data.constants import CIFAR10_CLASSES


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
