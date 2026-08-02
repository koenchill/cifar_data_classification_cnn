"""Guide Step 6: unnormalize and 8-image Actual/Predicted gallery."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch import Tensor
from torch.utils.data import DataLoader

from cifar_cnn.data.constants import CIFAR10_CLASSES


def unnormalize_guide(img: Tensor) -> Tensor:
    """Guide imshow helper: ``img / 2 + 0.5`` then clip to display range."""
    out = img / 2 + 0.5
    return out.clamp(0.0, 1.0)


def tensor_to_hwc(img: Tensor) -> Tensor:
    """CHW → HWC for matplotlib."""
    if img.ndim != 3:
        raise ValueError(f"Expected CHW tensor, got shape {tuple(img.shape)}")
    return img.permute(1, 2, 0)


def predict_batch(
    model: nn.Module,
    images: Tensor,
    *,
    device: str | torch.device = "cpu",
) -> tuple[Tensor, Tensor]:
    """Return predicted class indices and softmax confidences."""
    device = torch.device(device)
    model = model.to(device)
    model.eval()
    with torch.no_grad():
        outputs = model(images.to(device))
        confidences, predicted = torch.max(F.softmax(outputs, dim=1), 1)
    return predicted.cpu(), confidences.cpu()


def save_prediction_gallery(
    model: nn.Module,
    testloader: DataLoader[Any],
    path: str | Path,
    *,
    n_images: int = 8,
    class_names: tuple[str, ...] = CIFAR10_CLASSES,
    device: str | torch.device = "cpu",
) -> Path:
    """Save an 8-image gallery with Actual/Predicted class-name titles."""
    if n_images != 8:
        raise ValueError("Guide Step 6 requires exactly 8 gallery images")

    images_list: list[Tensor] = []
    labels_list: list[int] = []
    for images, labels in testloader:
        for i in range(images.size(0)):
            images_list.append(images[i])
            labels_list.append(int(labels[i].item()))
            if len(images_list) >= n_images:
                break
        if len(images_list) >= n_images:
            break

    if len(images_list) < n_images:
        raise ValueError(f"Need {n_images} test images; got {len(images_list)}")

    batch = torch.stack(images_list[:n_images])
    predicted, confidences = predict_batch(model, batch, device=device)

    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(2, 4, figsize=(12, 6))
    for idx, ax in enumerate(axes.flat):
        img = tensor_to_hwc(unnormalize_guide(batch[idx].cpu()))
        actual_name = class_names[labels_list[idx]]
        pred_name = class_names[int(predicted[idx].item())]
        correct = labels_list[idx] == int(predicted[idx].item())
        conf = float(confidences[idx].item())
        ax.imshow(img.numpy())
        ax.set_title(
            f"Actual: {actual_name}\nPredicted: {pred_name}\n"
            f"{'OK' if correct else 'MISS'} conf={conf:.2f}",
            fontsize=8,
        )
        ax.axis("off")
    fig.tight_layout()
    fig.savefig(out, dpi=120)
    plt.close(fig)
    return out
