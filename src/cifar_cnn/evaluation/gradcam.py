"""Grad-CAM for last convolutional feature map (limitations documented)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import torch.nn as nn
import torch.nn.functional as F
from torch import Tensor

from cifar_cnn.evaluation.viz import unnormalize_guide


@dataclass
class GradCAMResult:
    class_idx: int
    heatmap: Tensor  # (H, W) in [0, 1]
    overlay_path: str | None = None


class GradCAM:
    """Grad-CAM using gradients of the target class score w.r.t. a conv map."""

    def __init__(self, model: nn.Module, target_layer: nn.Module) -> None:
        self.model = model
        self.target_layer = target_layer
        self._activations: Tensor | None = None
        self._gradients: Tensor | None = None
        self._handles = [
            target_layer.register_forward_hook(self._forward_hook),
            target_layer.register_full_backward_hook(self._backward_hook),
        ]

    def _forward_hook(self, _module: nn.Module, _inp: Any, out: Tensor) -> None:
        self._activations = out.detach()

    def _backward_hook(
        self,
        _module: nn.Module,
        _gin: tuple[Tensor, ...] | Tensor,
        gout: tuple[Tensor, ...] | Tensor,
    ) -> None:
        grad = gout[0] if isinstance(gout, tuple) else gout
        self._gradients = grad.detach()

    def close(self) -> None:
        for h in self._handles:
            h.remove()

    def __call__(self, x: Tensor, *, class_idx: int | None = None) -> GradCAMResult:
        self.model.eval()
        x = x.detach().requires_grad_(True)
        logits = self.model(x)
        if class_idx is None:
            class_idx = int(logits.argmax(dim=1).item())
        self.model.zero_grad(set_to_none=True)
        score = logits[0, class_idx]
        score.backward()
        if self._activations is None or self._gradients is None:
            raise RuntimeError("Grad-CAM hooks did not capture activations/gradients")
        weights = self._gradients.mean(dim=(2, 3), keepdim=True)
        cam = (weights * self._activations).sum(dim=1, keepdim=True)
        cam = F.relu(cam)
        cam = F.interpolate(cam, size=x.shape[-2:], mode="bilinear", align_corners=False)
        cam = cam[0, 0]
        cam = cam - cam.min()
        cam = cam / (cam.max() + 1e-8)
        return GradCAMResult(class_idx=class_idx, heatmap=cam.detach().cpu())


def resolve_target_layer(model: nn.Module) -> nn.Module:
    layer = getattr(model, "conv3", None)
    if isinstance(layer, nn.Module):
        return layer
    raise AttributeError("Model has no conv3 layer for default Grad-CAM target")


def save_gradcam_overlay(
    image_chw: Tensor,
    result: GradCAMResult,
    path: str | Path,
    *,
    title: str,
) -> Path:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    img = unnormalize_guide(image_chw.detach().cpu()).permute(1, 2, 0).numpy()
    heat = result.heatmap.numpy()
    fig, axes = plt.subplots(1, 3, figsize=(9, 3))
    axes[0].imshow(img)
    axes[0].set_title("Input")
    axes[1].imshow(heat, cmap="jet")
    axes[1].set_title(f"Grad-CAM cls={result.class_idx}")
    axes[2].imshow(img)
    axes[2].imshow(heat, cmap="jet", alpha=0.45)
    axes[2].set_title(title)
    for ax in axes:
        ax.axis("off")
    fig.suptitle(
        "Limitation: Grad-CAM is explanatory localization, not a causal proof",
        fontsize=8,
    )
    fig.tight_layout()
    fig.savefig(out, dpi=120)
    plt.close(fig)
    result.overlay_path = str(out)
    return out
